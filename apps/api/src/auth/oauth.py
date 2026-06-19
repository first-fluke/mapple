"""OAuth provider configuration and JWKS-based id_token verification.

Supported providers: google, github, apple.
Apple Sign-In uses a client_secret derived from a signed ES256 JWT (team/key ids +
private key) and verifies the id_token via Apple's JWKS endpoint.
"""

import hashlib
import os
import time
from typing import Any, cast

import httpx
import jwt

# ---------------------------------------------------------------------------
# Provider metadata
# ---------------------------------------------------------------------------

PROVIDER_CONFIG: dict[str, dict[str, str]] = {
    "google": {
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
        "client_id_env": "GOOGLE_CLIENT_ID",
        "client_secret_env": "GOOGLE_CLIENT_SECRET",
        "scope": "openid email profile",
    },
    "github": {
        "authorization_endpoint": "https://github.com/login/oauth/authorize",
        "token_endpoint": "https://github.com/login/oauth/access_token",
        # GitHub does not support OIDC id_token — use user API instead.
        "user_endpoint": "https://api.github.com/user",
        "user_email_endpoint": "https://api.github.com/user/emails",
        "client_id_env": "GITHUB_CLIENT_ID",
        "client_secret_env": "GITHUB_CLIENT_SECRET",
        "scope": "read:user user:email",
    },
}

SUPPORTED_PROVIDERS = frozenset(PROVIDER_CONFIG.keys())

# ---------------------------------------------------------------------------
# Apple Sign-In configuration
# ---------------------------------------------------------------------------

APPLE_JWKS_URI = "https://appleid.apple.com/auth/keys"
APPLE_TOKEN_ENDPOINT = "https://appleid.apple.com/auth/token"
APPLE_ISSUER = "https://appleid.apple.com"


def _apple_credentials_present() -> bool:
    """Return True when all four Apple credentials are set in the environment."""
    return all(
        os.getenv(k)
        for k in ("APPLE_CLIENT_ID", "APPLE_TEAM_ID", "APPLE_KEY_ID", "APPLE_PRIVATE_KEY")
    )


def _build_apple_client_secret() -> str:
    """Build the signed ES256 client_secret JWT required by Apple's token endpoint.

    Apple requires a JWT signed with the app's private key (ES256) instead of
    a static client secret.  The JWT payload follows Apple's specification:
      iss  = Team ID
      iat  = now
      exp  = now + 180 days (max allowed)
      aud  = https://appleid.apple.com
      sub  = Client ID (Services ID / bundle ID)

    The token is signed with the private key identified by Key ID (kid header).

    Raises RuntimeError if any required env var is missing.
    """
    client_id = os.getenv("APPLE_CLIENT_ID", "")
    team_id = os.getenv("APPLE_TEAM_ID", "")
    key_id = os.getenv("APPLE_KEY_ID", "")
    private_key_raw = os.getenv("APPLE_PRIVATE_KEY", "")

    if not all([client_id, team_id, key_id, private_key_raw]):
        raise RuntimeError("Apple Sign-In credentials not fully configured in environment")

    # Support escaped newlines in env var values (common in Docker/CI)
    private_key = private_key_raw.replace("\\n", "\n")

    now = int(time.time())
    payload = {
        "iss": team_id,
        "iat": now,
        "exp": now + 15552000,  # 180 days
        "aud": APPLE_ISSUER,
        "sub": client_id,
    }
    return jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"kid": key_id},
    )


def get_client_id(provider: str) -> str:
    cfg = PROVIDER_CONFIG[provider]
    value = os.getenv(cfg["client_id_env"], "")
    if not value:
        raise RuntimeError(f"Missing env var: {cfg['client_id_env']}")
    return value


def get_client_secret(provider: str) -> str:
    cfg = PROVIDER_CONFIG[provider]
    value = os.getenv(cfg["client_secret_env"], "")
    if not value:
        raise RuntimeError(f"Missing env var: {cfg['client_secret_env']}")
    return value


# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------

def compute_code_challenge(code_verifier: str) -> str:
    """Compute S256 code challenge from verifier (RFC 7636)."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    import base64
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


# ---------------------------------------------------------------------------
# Authorization URL builder
# ---------------------------------------------------------------------------

def build_authorization_url(
    provider: str,
    state: str,
    code_challenge: str,
    nonce: str,
    redirect_uri: str,
) -> str:
    """Build the OAuth authorization URL with PKCE + nonce parameters."""
    from urllib.parse import urlencode

    cfg = PROVIDER_CONFIG[provider]
    params: dict[str, str] = {
        "client_id": get_client_id(provider),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": cfg["scope"],
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    if provider == "google":
        params["nonce"] = nonce
        params["access_type"] = "offline"
        params["prompt"] = "consent"

    return cfg["authorization_endpoint"] + "?" + urlencode(params)


# ---------------------------------------------------------------------------
# Token exchange
# ---------------------------------------------------------------------------

async def exchange_code_for_tokens(
    provider: str,
    code: str,
    code_verifier: str,
    redirect_uri: str,
) -> dict[str, Any]:
    """Exchange authorization code for provider tokens via PKCE."""
    cfg = PROVIDER_CONFIG[provider]
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": get_client_id(provider),
        "client_secret": get_client_secret(provider),
        "code_verifier": code_verifier,
    }
    headers = {}
    if provider == "github":
        headers["Accept"] = "application/json"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(cfg["token_endpoint"], data=data, headers=headers)
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())


# ---------------------------------------------------------------------------
# JWKS-based id_token verification (Google)
# ---------------------------------------------------------------------------

# Simple in-memory JWKS cache (invalidated per-request on key miss)
_jwks_cache: dict[str, Any] = {}


async def _fetch_jwks(jwks_uri: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(jwks_uri)
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())


async def verify_google_id_token(
    id_token: str,
    nonce: str,
    client_id: str,
) -> dict[str, Any]:
    """Verify Google id_token signature via JWKS and validate nonce.

    Returns the decoded claims dict on success.
    Raises jwt.InvalidTokenError subclasses on failure.
    """
    jwks_uri = PROVIDER_CONFIG["google"]["jwks_uri"]

    # Try cached JWKS first, refetch on kid miss
    jwks = _jwks_cache.get(jwks_uri)
    if not jwks:
        jwks = await _fetch_jwks(jwks_uri)
        _jwks_cache[jwks_uri] = jwks

    # Get kid from unverified header
    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header.get("kid")

    # Find matching public key
    public_key = _find_jwk(jwks, kid)
    if public_key is None:
        # Refetch once on key miss (key rotation)
        jwks = await _fetch_jwks(jwks_uri)
        _jwks_cache[jwks_uri] = jwks
        public_key = _find_jwk(jwks, kid)

    if public_key is None:
        raise jwt.InvalidKeyError(f"No matching JWK found for kid={kid}")

    claims = jwt.decode(
        id_token,
        public_key,
        algorithms=["RS256"],
        audience=client_id,
        options={"require": ["sub", "email", "exp", "iat", "nonce"]},
    )

    if claims.get("nonce") != nonce:
        raise jwt.InvalidTokenError("nonce mismatch — possible replay attack")

    return claims


def _find_jwk(jwks: dict[str, Any], kid: str | None) -> Any:
    """Return a PyJWT-compatible public key for the matching kid."""
    from jwt.algorithms import RSAAlgorithm

    keys = jwks.get("keys", [])
    for key_data in keys:
        if kid is None or key_data.get("kid") == kid:
            return RSAAlgorithm.from_jwk(key_data)
    return None


# ---------------------------------------------------------------------------
# GitHub user info (no OIDC id_token)
# ---------------------------------------------------------------------------

async def fetch_github_user_info(access_token: str) -> dict[str, Any]:
    """Fetch GitHub user profile and primary email."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        user_resp = await client.get(
            PROVIDER_CONFIG["github"]["user_endpoint"],
            headers=headers,
        )
        user_resp.raise_for_status()
        user_data = user_resp.json()

        email_resp = await client.get(
            PROVIDER_CONFIG["github"]["user_email_endpoint"],
            headers=headers,
        )
        email_resp.raise_for_status()
        emails = email_resp.json()

    primary_email = next(
        (e["email"] for e in emails if e.get("primary") and e.get("verified")),
        None,
    )
    if not primary_email:
        # Fallback: first verified email
        primary_email = next(
            (e["email"] for e in emails if e.get("verified")),
            user_data.get("email", ""),
        )

    return {
        "sub": str(user_data["id"]),
        "email": primary_email,
        "name": user_data.get("name") or user_data.get("login", ""),
        "picture": user_data.get("avatar_url", ""),
    }


# ---------------------------------------------------------------------------
# Apple Sign-In — id_token verification via JWKS
# ---------------------------------------------------------------------------

# Reuse the same in-memory JWKS cache pattern as Google.
_apple_jwks_cache: dict[str, Any] = {}


async def _fetch_apple_jwks() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(APPLE_JWKS_URI)
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())


def _find_apple_jwk(jwks: dict[str, Any], kid: str | None) -> Any:
    """Return a PyJWT-compatible public key for the matching Apple kid."""
    from jwt.algorithms import RSAAlgorithm

    keys = jwks.get("keys", [])
    for key_data in keys:
        if kid is None or key_data.get("kid") == kid:
            return RSAAlgorithm.from_jwk(key_data)
    return None


async def verify_apple_id_token(
    id_token: str,
    client_id: str,
) -> dict[str, Any]:
    """Verify an Apple id_token via Apple's JWKS and return the decoded claims.

    Apple id_tokens use RS256.  The nonce is NOT required for the mobile native
    exchange flow (where PKCE is used instead), so nonce validation is skipped here.
    For web flows the caller should validate the nonce separately.

    Raises jwt.InvalidTokenError subclasses on failure.
    """
    jwks = _apple_jwks_cache.get(APPLE_JWKS_URI)
    if not jwks:
        jwks = await _fetch_apple_jwks()
        _apple_jwks_cache[APPLE_JWKS_URI] = jwks

    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header.get("kid")

    public_key = _find_apple_jwk(jwks, kid)
    if public_key is None:
        # Refetch once on key miss (key rotation)
        jwks = await _fetch_apple_jwks()
        _apple_jwks_cache[APPLE_JWKS_URI] = jwks
        public_key = _find_apple_jwk(jwks, kid)

    if public_key is None:
        raise jwt.InvalidKeyError(f"No matching Apple JWK found for kid={kid}")

    claims = jwt.decode(
        id_token,
        public_key,
        algorithms=["RS256"],
        audience=client_id,
        issuer=APPLE_ISSUER,
        options={"require": ["sub", "email", "exp", "iat"]},
    )
    return claims


async def exchange_apple_code_for_tokens(
    code: str,
    code_verifier: str,
    redirect_uri: str,
) -> dict[str, Any]:
    """Exchange an Apple authorization code for provider tokens."""
    client_id = os.getenv("APPLE_CLIENT_ID", "")
    if not client_id:
        raise RuntimeError("APPLE_CLIENT_ID not configured")

    client_secret = _build_apple_client_secret()
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
        "code_verifier": code_verifier,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(APPLE_TOKEN_ENDPOINT, data=data)
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())
