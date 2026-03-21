import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_organization(client: AsyncClient, auth_headers: dict):
    """Test creating an organization."""
    response = await client.post(
        "/organizations",
        json={"name": "Acme Corp", "type": "company"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Acme Corp"
    assert data["type"] == "company"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_organization_requires_auth(client: AsyncClient):
    """Test creating an organization requires authentication."""
    response = await client.post(
        "/organizations",
        json={"name": "Acme Corp", "type": "company"},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_duplicate_organization(client: AsyncClient, auth_headers: dict):
    """Test creating a duplicate organization returns 409."""
    payload = {"name": "DupeCo", "type": "company"}
    response1 = await client.post("/organizations", json=payload, headers=auth_headers)
    assert response1.status_code == 201

    response2 = await client.post("/organizations", json=payload, headers=auth_headers)
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_search_organizations(client: AsyncClient, auth_headers: dict):
    """Test searching organizations by name."""
    # Create a few organizations
    await client.post("/organizations", json={"name": "Alpha Inc", "type": "company"}, headers=auth_headers)
    await client.post("/organizations", json={"name": "Beta LLC", "type": "company"}, headers=auth_headers)
    await client.post("/organizations", json={"name": "Gamma Ltd", "type": "company"}, headers=auth_headers)

    # Search for "Alpha"
    response = await client.get("/organizations", params={"q": "Alpha"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1
    assert any(org["name"] == "Alpha Inc" for org in data)


@pytest.mark.asyncio
async def test_search_organizations_empty_query(client: AsyncClient, auth_headers: dict):
    """Test searching with empty query returns results."""
    response = await client.get("/organizations", params={"q": ""}, headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


@pytest.mark.asyncio
async def test_create_organization_validation(client: AsyncClient, auth_headers: dict):
    """Test organization creation validates input."""
    # Empty name should fail
    response = await client.post(
        "/organizations",
        json={"name": "", "type": "company"},
        headers=auth_headers,
    )
    assert response.status_code == 422

    # Missing type should fail
    response = await client.post(
        "/organizations",
        json={"name": "Test"},
        headers=auth_headers,
    )
    assert response.status_code == 422
