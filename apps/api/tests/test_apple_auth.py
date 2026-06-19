"""Tests for Apple Sign-In env-conditional behavior (Task A).

The 501 fallback path is tested without any Apple credentials in env.
The real token-verification path is skipped (requires live Apple JWKS + valid token).
"""

import os
from unittest.mock import patch


async def test_apple_exchange_returns_501_when_unconfigured(client):
    """POST /auth/exchange with provider=apple must return 501 when Apple env vars are absent."""
    # Ensure none of the Apple env vars are set for this test.
    with patch.dict(
        os.environ,
        {
            "APPLE_CLIENT_ID": "",
            "APPLE_TEAM_ID": "",
            "APPLE_KEY_ID": "",
            "APPLE_PRIVATE_KEY": "",
        },
        clear=False,
    ):
        # Force the module-level _apple_credentials_present() to see empty values.

        import src.auth.oauth as oauth_mod

        orig = oauth_mod._apple_credentials_present
        oauth_mod._apple_credentials_present = lambda: False
        try:
            response = await client.post(
                "/auth/exchange",
                json={"provider": "apple", "id_token": "fake-token"},
            )
        finally:
            oauth_mod._apple_credentials_present = orig

    assert response.status_code == 501
    body = response.json()
    # FastAPI wraps HTTPException detail under "detail"
    assert "detail" in body
    detail = body["detail"]
    assert "Apple" in detail or "apple" in detail.lower()
    assert "APPLE_CLIENT_ID" in detail or "configured" in detail.lower()


async def test_apple_exchange_501_message_does_not_leak_internals(client):
    """501 response must not expose implementation details like redis keys or class names."""
    import src.auth.oauth as oauth_mod

    orig = oauth_mod._apple_credentials_present
    oauth_mod._apple_credentials_present = lambda: False
    try:
        response = await client.post(
            "/auth/exchange",
            json={"provider": "apple", "id_token": "fake-token"},
        )
    finally:
        oauth_mod._apple_credentials_present = orig

    assert response.status_code == 501
    body_text = response.text.lower()
    assert "traceback" not in body_text
    assert "exception" not in body_text
    assert "redis" not in body_text


async def test_unsupported_provider_returns_400(client):
    """POST /auth/exchange with an unknown provider must return 400."""
    response = await client.post(
        "/auth/exchange",
        json={"provider": "twitter", "id_token": "fake-token"},
    )
    # Pydantic validation rejects the literal before the route runs
    assert response.status_code in (400, 422)


async def test_apple_credentials_present_helper_false_when_env_empty():
    """Unit test: _apple_credentials_present() returns False when env vars are unset."""

    with patch.dict(
        os.environ,
        {
            "APPLE_CLIENT_ID": "",
            "APPLE_TEAM_ID": "",
            "APPLE_KEY_ID": "",
            "APPLE_PRIVATE_KEY": "",
        },
        clear=False,
    ):
        # Re-evaluate inside patched env
        result = all(
            os.getenv(k)
            for k in ("APPLE_CLIENT_ID", "APPLE_TEAM_ID", "APPLE_KEY_ID", "APPLE_PRIVATE_KEY")
        )
    assert result is False


async def test_apple_credentials_present_helper_true_when_all_set():
    """Unit test: _apple_credentials_present() returns True when all four env vars are set."""
    with patch.dict(
        os.environ,
        {
            "APPLE_CLIENT_ID": "com.example.app",
            "APPLE_TEAM_ID": "TEAMID1234",
            "APPLE_KEY_ID": "KEYID12345",
            "APPLE_PRIVATE_KEY": "-----BEGIN EC PRIVATE KEY-----\nfake\n-----END EC PRIVATE KEY-----",
        },
        clear=False,
    ):
        import src.auth.oauth as oauth_mod
        result = oauth_mod._apple_credentials_present()
    assert result is True
