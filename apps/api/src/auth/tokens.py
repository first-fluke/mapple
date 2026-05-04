"""Token issuance, verification, rotation, and invalidation.

access  : JWS HS256, stateless
refresh : opaque 32-byte URL-safe random, Redis-backed with family rotation
"""

import hashlib
import json
import os
import secrets
import time
from typing import Any

import jwt
from redis.asyncio import Redis

from src.lib.auth import JWT_ALGORITHM, JWT_AUDIENCE, JWT_ISSUER, JWT_SIGNING_KEY
from src.lib.exceptions import UnauthorizedException

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

JWT_ACCESS_TTL_SECONDS: int = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "900"))  # 15 min
JWT_REFRESH_TTL_SECONDS: int = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "2592000"))  # 30 days


# ---------------------------------------------------------------------------
# Access token
# ---------------------------------------------------------------------------


def issue_access(user_id: str) -> tuple[str, int]:
    """Issue a JWS HS256 access token.

    Returns (token, exp_unix).
    """
    now = int(time.time())
    exp = now + JWT_ACCESS_TTL_SECONDS
    payload: dict[str, Any] = {
        "sub": user_id,
        "exp": exp,
        "iat": now,
        "jti": secrets.token_urlsafe(16),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
    }
    token = jwt.encode(payload, JWT_SIGNING_KEY, algorithm=JWT_ALGORITHM)
    return token, exp


def verify_access(token: str) -> dict[str, Any]:
    """Verify and decode a JWS access token.

    Raises UnauthorizedException on any failure.
    """
    try:
        return jwt.decode(
            token,
            JWT_SIGNING_KEY,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"require": ["sub", "exp", "iat", "jti", "iss", "aud"]},
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(message="Access token expired")
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException(message=f"Invalid access token: {exc}")


# ---------------------------------------------------------------------------
# Refresh token helpers
# ---------------------------------------------------------------------------


def _token_hash(raw_token: str) -> str:
    """SHA-256 hash of raw token for use as Redis key (prevents plaintext dump exposure)."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def _refresh_key(token_hash: str) -> str:
    return f"refresh:{token_hash}"


def _family_key(family_id: str) -> str:
    return f"family:{family_id}"


# ---------------------------------------------------------------------------
# Refresh token issuance
# ---------------------------------------------------------------------------


async def issue_refresh(
    redis: Redis,
    user_id: str,
    family_id: str | None = None,
) -> tuple[str, str, int]:
    """Issue a new opaque refresh token.

    If family_id is None, a new family is created (first login).
    Returns (raw_token, family_id, exp_unix).
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = _token_hash(raw_token)
    family_id = family_id or secrets.token_urlsafe(16)
    exp_unix = int(time.time()) + JWT_REFRESH_TTL_SECONDS

    record = json.dumps({
        "user_id": user_id,
        "family_id": family_id,
        "used": False,
        "exp_unix": exp_unix,
    })

    pipe = redis.pipeline()
    pipe.set(_refresh_key(token_hash), record, ex=JWT_REFRESH_TTL_SECONDS)
    pipe.sadd(_family_key(family_id), token_hash)
    pipe.expire(_family_key(family_id), JWT_REFRESH_TTL_SECONDS)
    await pipe.execute()

    return raw_token, family_id, exp_unix


# ---------------------------------------------------------------------------
# Refresh token rotation
# ---------------------------------------------------------------------------


async def rotate_refresh(
    redis: Redis,
    raw_token: str,
) -> tuple[str, str, int, str]:
    """Rotate a refresh token.

    1. Validate token exists and is not used.
    2. If used → replay detected → invalidate entire family → 401.
    3. If valid → mark used → issue new token in same family.

    Returns (new_raw_token, user_id, exp_unix, family_id).
    Raises UnauthorizedException on any failure.
    """
    token_hash = _token_hash(raw_token)
    key = _refresh_key(token_hash)

    raw = await redis.get(key)
    if raw is None:
        raise UnauthorizedException(message="Refresh token not found or expired")

    record: dict[str, Any] = json.loads(raw)
    family_id: str = record["family_id"]
    user_id: str = record["user_id"]

    if record.get("used"):
        # Replay detected — invalidate entire family
        await invalidate_family(redis, family_id)
        raise UnauthorizedException(message="Refresh token already used — possible replay attack")

    # Mark current token as used
    record["used"] = True
    remaining_ttl = record["exp_unix"] - int(time.time())
    if remaining_ttl <= 0:
        raise UnauthorizedException(message="Refresh token expired")

    await redis.set(key, json.dumps(record), ex=remaining_ttl)

    # Issue new token in same family
    new_raw, _, new_exp = await issue_refresh(redis, user_id, family_id=family_id)
    return new_raw, user_id, new_exp, family_id


# ---------------------------------------------------------------------------
# Family invalidation (logout / replay)
# ---------------------------------------------------------------------------


async def invalidate_family(redis: Redis, family_id: str) -> None:
    """Delete all refresh tokens belonging to a family."""
    fkey = _family_key(family_id)
    token_hashes = await redis.smembers(fkey)

    if token_hashes:
        pipe = redis.pipeline()
        for th in token_hashes:
            pipe.delete(_refresh_key(th))
        pipe.delete(fkey)
        await pipe.execute()
    else:
        await redis.delete(fkey)


async def get_refresh_record(redis: Redis, raw_token: str) -> dict[str, Any] | None:
    """Return the refresh token record or None if not found."""
    token_hash = _token_hash(raw_token)
    raw = await redis.get(_refresh_key(token_hash))
    if raw is None:
        return None
    return json.loads(raw)
