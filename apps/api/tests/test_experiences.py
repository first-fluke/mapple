import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def seed_data(db_session: AsyncSession):
    """Insert a test user, contact, and organization for experience tests."""
    await db_session.execute(
        text(
            "INSERT INTO user_auth (id, provider, provider_id, email, name) "
            "VALUES (:id, :provider, :provider_id, :email, :name)"
        ),
        {"id": 1, "provider": "google", "provider_id": "123", "email": "test@example.com", "name": "Test User"},
    )
    await db_session.execute(
        text(
            "INSERT INTO contact (id, user_id, name, email) "
            "VALUES (:id, :user_id, :name, :email)"
        ),
        {"id": 1, "user_id": 1, "name": "John Doe", "email": "john@example.com"},
    )
    await db_session.execute(
        text(
            "INSERT INTO organization (id, name, type) "
            "VALUES (:id, :name, :type)"
        ),
        {"id": 1, "name": "Test Org", "type": "company"},
    )
    await db_session.commit()
    return {"user_id": 1, "contact_id": 1, "organization_id": 1}


@pytest.mark.asyncio
async def test_create_experience(client: AsyncClient, auth_headers: dict, seed_data: dict):
    """Test creating an experience for a contact."""
    contact_id = seed_data["contact_id"]
    org_id = seed_data["organization_id"]

    response = await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Engineer", "major": "CS"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["contact_id"] == contact_id
    assert data["organization_id"] == org_id
    assert data["role"] == "Engineer"
    assert data["major"] == "CS"


@pytest.mark.asyncio
async def test_list_experiences(client: AsyncClient, auth_headers: dict, seed_data: dict):
    """Test listing experiences for a contact."""
    contact_id = seed_data["contact_id"]
    org_id = seed_data["organization_id"]

    # Create two experiences
    await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Manager"},
        headers=auth_headers,
    )
    await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Director"},
        headers=auth_headers,
    )

    response = await client.get(f"/contacts/{contact_id}/experiences", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_experience(client: AsyncClient, auth_headers: dict, seed_data: dict):
    """Test updating an experience."""
    contact_id = seed_data["contact_id"]
    org_id = seed_data["organization_id"]

    create_resp = await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Intern"},
        headers=auth_headers,
    )
    experience_id = create_resp.json()["data"]["id"]

    response = await client.put(
        f"/contacts/{contact_id}/experiences/{experience_id}",
        json={"role": "Senior Engineer"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["role"] == "Senior Engineer"


@pytest.mark.asyncio
async def test_delete_experience(client: AsyncClient, auth_headers: dict, seed_data: dict):
    """Test deleting an experience."""
    contact_id = seed_data["contact_id"]
    org_id = seed_data["organization_id"]

    create_resp = await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Temp"},
        headers=auth_headers,
    )
    experience_id = create_resp.json()["data"]["id"]

    response = await client.delete(
        f"/contacts/{contact_id}/experiences/{experience_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    list_resp = await client.get(f"/contacts/{contact_id}/experiences", headers=auth_headers)
    assert all(e["id"] != experience_id for e in list_resp.json()["data"])


@pytest.mark.asyncio
async def test_experience_requires_auth(client: AsyncClient):
    """Test experience endpoints require authentication."""
    response = await client.get("/contacts/1/experiences")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_experience_not_found(client: AsyncClient, auth_headers: dict, seed_data: dict):
    """Test updating a non-existent experience returns 404."""
    contact_id = seed_data["contact_id"]

    response = await client.put(
        f"/contacts/{contact_id}/experiences/9999",
        json={"role": "Ghost"},
        headers=auth_headers,
    )
    assert response.status_code == 404
