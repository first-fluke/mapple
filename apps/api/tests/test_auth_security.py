"""Security tests for authentication and JWT handling.

Covers OWASP A01 (Broken Access Control), A02 (Cryptographic Failures),
A07 (Identification and Authentication Failures).
"""

import datetime

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
    assert response.json() == {"status": "ok"}


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
    # Create unsigned token with alg=none
    token = jwt.encode(payload, key="", algorithm="none")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code == 401


async def test_jwt_algorithm_confusion_attack(client):
    """JWT algorithm confusion (HS256 vs RS256) must be prevented.

    If the server expects HS256 but accepts RS256, an attacker could
    use the public key as the HMAC secret.
    """
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": "1",
        "email": "attacker@evil.com",
        "iat": now,
        "exp": now + datetime.timedelta(minutes=15),
    }
    # Sign with a different algorithm than what server expects
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
    # Create a valid token
    token = jwt.encode(
        {
            "sub": "1",
            "email": "user@test.com",
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(minutes=15),
        },
        JWT_TEST_SECRET,
        algorithm="HS256",
    )
    # Tamper with the token by modifying the payload portion
    parts = token.split(".")
    import base64

    # Decode payload, change sub, re-encode
    padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
    payload_bytes = base64.urlsafe_b64decode(padded)
    tampered = payload_bytes.replace(b'"1"', b'"999"')
    parts[1] = base64.urlsafe_b64encode(tampered).rstrip(b"=").decode()
    tampered_token = ".".join(parts)

    headers = {"Authorization": f"Bearer {tampered_token}"}
    response = await client.get("/organizations", headers=headers)
    assert response.status_code == 401


# --- A07: Refresh token security ---


async def test_refresh_token_rotation(client, db_session, fake_redis):
    """Old refresh token must be invalidated after rotation."""
    user = await create_test_user(db_session)

    # Store a refresh token in Redis
    old_token = "old-refresh-token-123"
    await fake_redis.set(f"refresh:{old_token}", str(user.id), ex=86400)

    # Refresh with old token
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": old_token},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    new_token = data["refresh_token"]

    # Old token must be invalid now
    assert await fake_redis.get(f"refresh:{old_token}") is None

    # New token must be valid
    assert await fake_redis.get(f"refresh:{new_token}") == str(user.id)


async def test_logout_invalidates_refresh_token(client, fake_redis):
    """Logout must delete the refresh token from storage."""
    token = "active-refresh-token"
    await fake_redis.set(f"refresh:{token}", "1", ex=86400)

    response = await client.request(
        "DELETE",
        "/auth/logout",
        json={"refresh_token": token},
    )
    assert response.status_code == 200

    # Token must be removed
    assert await fake_redis.get(f"refresh:{token}") is None


async def test_invalid_refresh_token_rejected(client, fake_redis):
    """Non-existent refresh tokens must be rejected."""
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": "nonexistent-token"},
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

    # This test documents the risk. In production, JWT_SECRET must be set.
    # If JWT_SECRET is the test value, it's been properly overridden.
    # If it were empty, any attacker could forge valid tokens.
    if JWT_SECRET == "":
        pytest.fail(
            "CRITICAL: JWT_SECRET is empty. "
            "Any attacker can forge valid JWT tokens. "
            "Set JWT_SECRET to a strong random value in production."
        )
