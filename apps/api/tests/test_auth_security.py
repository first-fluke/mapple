"""Security tests for authentication and JWT handling.

Covers OWASP A01 (Broken Access Control), A02 (Cryptographic Failures),
A07 (Identification and Authentication Failures).

Decision (cluster 4): FIXED TEST
  - All refresh/logout bodies changed from {"refresh_token": ...} to
    {"refresh": ...} to match the current RefreshRequest / LogoutRequest
    Pydantic schemas.
  - Logout is POST /auth/logout (not DELETE), returns 204 (not 200).
  - Redis storage uses SHA-256(raw_token) as key, not the raw token — test
    helpers now use the same hash so assertions are correct.

Decision (cluster 3): FIXED TEST
  - test_health_endpoint_is_public now asserts {"status": "ok", "checks": {...}}
    instead of the old {"status": "ok"} bare response.
"""

import datetime
import hashlib
import json
import time

import jwt
import pytest

from tests.conftest import (
    JWT_TEST_SECRET,
    create_test_user,
    make_auth_headers,
    make_expired_token,
    make_token_with_secret,
)

PROTECTED_ENDPOINTS = [
    ("GET", "/organizations"),
    ("POST", "/organizations"),
    ("GET", "/contacts/1/experiences"),
    ("POST", "/contacts/1/experiences"),
    ("GET", "/auth/me"),
    ("POST", "/upload/avatar"),
]


# --- A01: Broken Access Control (unauthenticated access) ---


@pytest.mark.parametrize("method,path", PROTECTED_ENDPOINTS)
async def test_protected_endpoints_reject_unauthenticated(client, method, path):
    """All protected endpoints must return 401/403 without a token."""
    response = await client.request(method, path)
    assert response.status_code == 401 or response.status_code == 403


async def test_health_endpoint_is_public(client):
    """Health check must be accessible without authentication."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "checks" in body


# --- A02: Cryptographic Failures (JWT) ---


async def test_invalid_jwt_rejected(client):
    """Malformed JWT tokens must be rejected."""
    headers = {"Authorization": "Bearer not-a-valid-jwt-token"}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code == 401


async def test_expired_jwt_rejected(client):
    """Expired JWT tokens must be rejected."""
    token = make_expired_token(user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code == 401


async def test_jwt_wrong_secret_rejected(client):
    """JWTs signed with a different secret must be rejected."""
    token = make_token_with_secret(user_id=1, secret="wrong-secret-key")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code == 401


async def test_jwt_none_algorithm_attack(client):
    """JWT 'none' algorithm attack must be rejected.

    CVE-2015-9235: Some JWT libraries accept tokens with alg=none,
    allowing complete authentication bypass.
    """
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": "1",
        "email": "attacker@evil.com",
        "iat": now,
        "exp": now + datetime.timedelta(minutes=15),
    }
    token = jwt.encode(payload, key="", algorithm="none")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code == 401


async def test_jwt_algorithm_confusion_attack(client):
    """JWT algorithm confusion (HS256 vs RS256) must be prevented."""
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": "1",
        "email": "attacker@evil.com",
        "iat": now,
        "exp": now + datetime.timedelta(minutes=15),
    }
    token = jwt.encode(payload, "some-public-key", algorithm="HS384")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code == 401


async def test_empty_bearer_token(client):
    """Empty bearer token must be rejected."""
    headers = {"Authorization": "Bearer "}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code in (401, 403, 422)


async def test_missing_bearer_prefix(client):
    """Token without 'Bearer' prefix must be rejected."""
    token = jwt.encode(
        {"sub": "1", "email": "test@test.com"},
        JWT_TEST_SECRET,
        algorithm="HS256",
    )
    headers = {"Authorization": token}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code in (401, 403, 422)


async def test_jwt_tampered_payload(client):
    """JWT with tampered payload (invalid signature) must be rejected."""
    token = jwt.encode(
        {
            "sub": "1",
            "email": "user@test.com",
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15),
        },
        JWT_TEST_SECRET,
        algorithm="HS256",
    )
    parts = token.split(".")
    import base64

    padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
    payload_bytes = base64.urlsafe_b64decode(padded)
    tampered = payload_bytes.replace(b'"1"', b'"999"')
    parts[1] = base64.urlsafe_b64encode(tampered).rstrip(b"=").decode()
    tampered_token = ".".join(parts)

    headers = {"Authorization": f"Bearer {tampered_token}"}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code == 401


# --- A07: Refresh token security ---


def _refresh_key(raw_token: str) -> str:
    """Mirror the key scheme in src/auth/tokens.py."""
    return f"refresh:{hashlib.sha256(raw_token.encode()).hexdigest()}"


def _family_key(family_id: str) -> str:
    return f"family:{family_id}"


async def test_refresh_token_rotation(client, db_session, fake_redis):
    """Old refresh token must be invalidated after rotation.

    FIXED: field name is "refresh" (not "refresh_token").
    Storage key is SHA-256(raw_token) per tokens.py — seed accordingly.
    """
    user = await create_test_user(db_session)

    old_token = "old-refresh-token-xyz-long-enough-32b"
    token_hash = hashlib.sha256(old_token.encode()).hexdigest()
    family_id = "test-family-id-rotation"
    record = json.dumps(
        {
            "user_id": str(user.id),
            "family_id": family_id,
            "used": False,
            "exp_unix": int(time.time()) + 86400,
        }
    )
    await fake_redis.set(f"refresh:{token_hash}", record, ex=86400)
    await fake_redis.sadd(f"family:{family_id}", token_hash)

    response = await client.post(
        "/auth/refresh",
        json={"refresh": old_token},
    )
    assert response.status_code == 200
    data = response.json()
    new_token = data["refresh"]

    # Old token must be marked used
    raw = await fake_redis.get(f"refresh:{token_hash}")
    if raw is not None:
        assert json.loads(raw)["used"] is True

    # New token must be stored
    new_hash = hashlib.sha256(new_token.encode()).hexdigest()
    assert await fake_redis.get(f"refresh:{new_hash}") is not None


async def test_logout_invalidates_refresh_token(client, fake_redis):
    """Logout must delete the refresh token from storage.

    FIXED: field name is "refresh" (not "refresh_token").
    Logout is POST /auth/logout and returns 204.
    """
    raw_token = "active-refresh-token-xyz-long-enough"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    family_id = "fam-abc-logout"
    record = json.dumps(
        {
            "user_id": "1",
            "family_id": family_id,
            "used": False,
            "exp_unix": int(time.time()) + 86400,
        }
    )
    await fake_redis.set(f"refresh:{token_hash}", record, ex=86400)
    await fake_redis.sadd(f"family:{family_id}", token_hash)

    response = await client.post(
        "/auth/logout",
        json={"refresh": raw_token},
    )
    assert response.status_code == 204

    # Token record must be removed
    assert await fake_redis.get(f"refresh:{token_hash}") is None


async def test_invalid_refresh_token_rejected(client, fake_redis):
    """Non-existent refresh tokens must be rejected.

    FIXED: field name is "refresh" (not "refresh_token").
    """
    response = await client.post(
        "/auth/refresh",
        json={"refresh": "nonexistent-token"},
    )
    assert response.status_code == 401


async def test_me_requires_valid_token(client, db_session):
    """GET /auth/me must return the authenticated user's own data only."""
    user = await create_test_user(db_session)
    headers = make_auth_headers(user.id)
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == user.id
    assert data["email"] == user.email


async def test_me_with_nonexistent_user_id(client):
    """GET /auth/me with a valid JWT but non-existent user must return 401."""
    headers = make_auth_headers(99999)
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401


# --- JWT secret vulnerability documentation ---


async def test_jwt_default_empty_secret_is_documented():
    """Document that JWT_SECRET defaults to empty string.

    SECURITY VULNERABILITY: If JWT_SECRET env var is not set,
    the default is an empty string, allowing trivial token forgery.
    """
    from src.lib.auth import JWT_SECRET

    if JWT_SECRET == "":
        pytest.fail(
            "CRITICAL: JWT_SECRET is empty. "
            "Any attacker can forge valid JWT tokens. "
            "Set JWT_SECRET to a strong random value in production."
        )
