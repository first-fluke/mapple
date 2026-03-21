import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_auth_callback(client: AsyncClient):
    """Test OAuth callback returns code and state."""
    response = await client.get("/auth/callback", params={"code": "test-code", "state": "test-state"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["code"] == "test-code"
    assert data["state"] == "test-state"


@pytest.mark.asyncio
async def test_auth_callback_without_state(client: AsyncClient):
    """Test OAuth callback works without optional state parameter."""
    response = await client.get("/auth/callback", params={"code": "test-code"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["code"] == "test-code"
    assert data["state"] is None


@pytest.mark.asyncio
async def test_auth_me_requires_authentication(client: AsyncClient):
    """Test /auth/me rejects requests without token."""
    response = await client.get("/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_auth_me_with_valid_token(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    """Test /auth/me returns user profile with valid token."""
    await db_session.execute(
        text(
            "INSERT INTO user_auth (id, provider, provider_id, email, name) "
            "VALUES (:id, :provider, :provider_id, :email, :name)"
        ),
        {"id": 1, "provider": "google", "provider_id": "123", "email": "test@example.com", "name": "Test User"},
    )
    await db_session.commit()

    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert data["provider"] == "google"


@pytest.mark.asyncio
async def test_auth_me_with_invalid_token(client: AsyncClient):
    """Test /auth/me returns 401 with invalid token."""
    response = await client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
