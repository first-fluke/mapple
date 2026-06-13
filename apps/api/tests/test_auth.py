"""Tests for auth endpoints.

Decision cluster 2:
  - test_auth_callback*: FIXED TEST — real route is GET /auth/callback/{provider},
    not /auth/callback. Tests updated to use /auth/callback/google. The callback
    always redirects (302) in the real impl; these tests verify the route exists
    (not 404) and that the redirect behaviour is correct.

Decision cluster 1 (shared with test_experiences.py):
  - test_auth_me_with_valid_token: FIXED TEST — old fixture used INSERT INTO
    user_auth; model maps User to table "user". Using ORM helper instead.
    Also removed assertion for 'provider' field which does not exist in UserOut.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_test_user, make_auth_headers


@pytest.mark.asyncio
async def test_auth_callback(client: AsyncClient):
    """OAuth callback redirects — the real route is /auth/callback/{provider}.

    In the test ASGI environment the OAuth state lookup will fail (Redis is
    faked and no state was stored), so the endpoint redirects to the error URL.
    We verify the route exists (not 404) and returns a redirect.
    """
    response = await client.get(
        "/auth/callback/google",
        params={"code": "test-code", "state": "test-state"},
        follow_redirects=False,
    )
    # Must NOT be 404 — route exists; a redirect (3xx) is the expected behaviour.
    assert response.status_code != 404
    assert response.status_code in (302, 303, 307, 308)


@pytest.mark.asyncio
async def test_auth_callback_without_state(client: AsyncClient):
    """OAuth callback with missing state: FastAPI returns 422 (required param)."""
    response = await client.get(
        "/auth/callback/google",
        params={"code": "test-code"},
        follow_redirects=False,
    )
    # state is a required Query param — FastAPI rejects it before routing logic.
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_me_requires_authentication(client: AsyncClient):
    """Test /auth/me rejects requests without token."""
    response = await client.get("/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_auth_me_with_valid_token(client: AsyncClient, db_session: AsyncSession):
    """Test /auth/me returns user profile with valid token.

    FIXED: was inserting into user_auth (old schema). Now uses ORM helper
    against the real 'user' table. Removed assertion for 'provider' which is
    not part of the UserOut schema.
    """
    user = await create_test_user(
        db_session,
        email="test@example.com",
        name="Test User",
    )
    headers = make_auth_headers(user.id)

    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    # 'provider' is not a UserOut field — the model only has id/email/name/image
    assert "id" in data


@pytest.mark.asyncio
async def test_auth_me_with_invalid_token(client: AsyncClient):
    """Test /auth/me returns 401 with invalid token."""
    response = await client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
