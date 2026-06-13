"""Tests for experiences endpoints.

The seed_data fixture uses ORM helpers from conftest so it always inserts into
whatever table the *current* models define — not a stale raw-SQL table name.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import (
    create_test_contact,
    create_test_organization,
    create_test_user,
    make_auth_headers,
)


@pytest.fixture
async def seed_data(db_session: AsyncSession):
    """Insert a test user, contact, and organization for experience tests.

    Decision: FIXED TEST — the original fixture used `user_auth` (old schema).
    The model now maps User to table "user". We use the ORM helper to stay
    schema-agnostic and avoid a repeat of this breakage.
    """
    user = await create_test_user(db_session)
    contact = await create_test_contact(db_session, user_id=user.id)
    org = await create_test_organization(db_session)
    return {"user_id": user.id, "contact_id": contact.id, "organization_id": org.id}


@pytest.mark.asyncio
async def test_create_experience(client: AsyncClient, seed_data: dict):
    """Test creating an experience for a contact."""
    contact_id = seed_data["contact_id"]
    org_id = seed_data["organization_id"]
    auth = make_auth_headers(seed_data["user_id"])

    response = await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Engineer", "major": "CS"},
        headers=auth,
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["contact_id"] == contact_id
    assert data["organization_id"] == org_id
    assert data["role"] == "Engineer"
    assert data["major"] == "CS"


@pytest.mark.asyncio
async def test_list_experiences(client: AsyncClient, seed_data: dict):
    """Test listing experiences for a contact."""
    contact_id = seed_data["contact_id"]
    org_id = seed_data["organization_id"]
    auth = make_auth_headers(seed_data["user_id"])

    # Create two experiences
    await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Manager"},
        headers=auth,
    )
    await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Director"},
        headers=auth,
    )

    response = await client.get(f"/contacts/{contact_id}/experiences", headers=auth)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_experience(client: AsyncClient, seed_data: dict):
    """Test updating an experience."""
    contact_id = seed_data["contact_id"]
    org_id = seed_data["organization_id"]
    auth = make_auth_headers(seed_data["user_id"])

    create_resp = await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Intern"},
        headers=auth,
    )
    experience_id = create_resp.json()["data"]["id"]

    response = await client.put(
        f"/contacts/{contact_id}/experiences/{experience_id}",
        json={"role": "Senior Engineer"},
        headers=auth,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["role"] == "Senior Engineer"


@pytest.mark.asyncio
async def test_delete_experience(client: AsyncClient, seed_data: dict):
    """Test deleting an experience."""
    contact_id = seed_data["contact_id"]
    org_id = seed_data["organization_id"]
    auth = make_auth_headers(seed_data["user_id"])

    create_resp = await client.post(
        f"/contacts/{contact_id}/experiences",
        json={"organization_id": org_id, "role": "Temp"},
        headers=auth,
    )
    experience_id = create_resp.json()["data"]["id"]

    response = await client.delete(
        f"/contacts/{contact_id}/experiences/{experience_id}",
        headers=auth,
    )
    assert response.status_code == 204

    list_resp = await client.get(f"/contacts/{contact_id}/experiences", headers=auth)
    assert all(e["id"] != experience_id for e in list_resp.json()["data"])


@pytest.mark.asyncio
async def test_experience_requires_auth(client: AsyncClient):
    """Test experience endpoints require authentication."""
    response = await client.get("/contacts/1/experiences")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_experience_not_found(client: AsyncClient, seed_data: dict):
    """Test updating a non-existent experience returns 404."""
    contact_id = seed_data["contact_id"]
    auth = make_auth_headers(seed_data["user_id"])

    response = await client.put(
        f"/contacts/{contact_id}/experiences/9999",
        json={"role": "Ghost"},
        headers=auth,
    )
    assert response.status_code == 404
