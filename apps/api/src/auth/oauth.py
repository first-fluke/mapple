"""OAuth provider configuration and JWKS-based id_token verification.

지원 provider: google, github
Apple OAuth는 Task L11에서 추가 예정.
"""

import hashlib
import os
from typing import Any

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
        # GitHub은 OIDC id_token 미지원. user API로 대체.
        "user_endpoint": "https://api.github.com/user",
        "user_email_endpoint": "https://api.github.com/user/emails",
        "client_id_env": "GITHUB_CLIENT_ID",
        "client_secret_env": "GITHUB_CLIENT_SECRET",
        "scope": "read:user user:email",
    },
}

SUPPORTED_PROVIDERS = frozenset(PROVIDER_CONFIG.keys())


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
        return resp.json()


# ---------------------------------------------------------------------------
# JWKS-based id_token verification (Google)
# ---------------------------------------------------------------------------

# Simple in-memory JWKS cache (invalidated per-request on key miss)
_jwks_cache: dict[str, Any] = {}


async def _fetch_jwks(jwks_uri: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(jwks_uri)
        resp.raise_for_status()
        return resp.json()


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
        raise jwt.InvalidClaimError("nonce mismatch — possible replay attack")

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
