"""Regression tests for the contact_relationships router (Task B).

Covers:
- Create a relationship edge (POST /contact-relationships).
- List relationships for a contact (GET /contact-relationships/contacts/{id}).
- Delete a relationship (DELETE /contact-relationships/{id}).
- A user cannot touch another user's relationships (isolation).
- Unauthenticated requests are rejected.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_test_contact, create_test_user, make_auth_headers


@pytest.mark.asyncio
async def test_create_relationship(client: AsyncClient, db_session: AsyncSession):
    """Creating a relationship edge returns 201 with the created record."""
    user = await create_test_user(db_session, email="rel1@test.com")
    c1 = await create_test_contact(db_session, user_id=user.id, name="Alice")
    c2 = await create_test_contact(db_session, user_id=user.id, name="Bob")

    response = await client.post(
        "/contact-relationships",
        json={"contact_id_1": c1.id, "contact_id_2": c2.id, "strength": 3.5},
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["user_id"] == user.id
    assert data["strength"] == pytest.approx(3.5)
    assert set([data["contact_id_1"], data["contact_id_2"]]) == {c1.id, c2.id}


@pytest.mark.asyncio
async def test_create_relationship_ids_ordered(
    client: AsyncClient, db_session: AsyncSession
):
    """The DB constraint requires contact_id_1 < contact_id_2; the service enforces this."""
    user = await create_test_user(db_session, email="rel2@test.com")
    c1 = await create_test_contact(db_session, user_id=user.id, name="A")
    c2 = await create_test_contact(db_session, user_id=user.id, name="B")

    # Send with reversed order on purpose
    response = await client.post(
        "/contact-relationships",
        json={"contact_id_1": max(c1.id, c2.id), "contact_id_2": min(c1.id, c2.id), "strength": 1.0},
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    # Service must normalize ordering
    assert data["contact_id_1"] < data["contact_id_2"]


@pytest.mark.asyncio
async def test_list_relationships_for_contact(
    client: AsyncClient, db_session: AsyncSession
):
    """Listing relationships for a contact returns all edges involving that contact."""
    user = await create_test_user(db_session, email="rel3@test.com")
    c1 = await create_test_contact(db_session, user_id=user.id, name="A")
    c2 = await create_test_contact(db_session, user_id=user.id, name="B")
    c3 = await create_test_contact(db_session, user_id=user.id, name="C")

    headers = make_auth_headers(user.id)
    await client.post(
        "/contact-relationships",
        json={"contact_id_1": c1.id, "contact_id_2": c2.id, "strength": 2.0},
        headers=headers,
    )
    await client.post(
        "/contact-relationships",
        json={"contact_id_1": c1.id, "contact_id_2": c3.id, "strength": 1.0},
        headers=headers,
    )

    response = await client.get(
        f"/contact-relationships/contacts/{c1.id}",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_relationships_empty(client: AsyncClient, db_session: AsyncSession):
    """Contact with no relationships returns an empty list, not 404."""
    user = await create_test_user(db_session, email="rel4@test.com")
    c1 = await create_test_contact(db_session, user_id=user.id, name="Lonely")

    response = await client.get(
        f"/contact-relationships/contacts/{c1.id}",
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.asyncio
async def test_delete_relationship(client: AsyncClient, db_session: AsyncSession):
    """Deleting a relationship returns 204 and the edge is gone."""
    user = await create_test_user(db_session, email="rel5@test.com")
    c1 = await create_test_contact(db_session, user_id=user.id, name="A")
    c2 = await create_test_contact(db_session, user_id=user.id, name="B")
    headers = make_auth_headers(user.id)

    create_resp = await client.post(
        "/contact-relationships",
        json={"contact_id_1": c1.id, "contact_id_2": c2.id, "strength": 1.0},
        headers=headers,
    )
    rel_id = create_resp.json()["data"]["id"]

    delete_resp = await client.delete(
        f"/contact-relationships/{rel_id}",
        headers=headers,
    )
    assert delete_resp.status_code == 204

    # Confirm gone
    list_resp = await client.get(
        f"/contact-relationships/contacts/{c1.id}",
        headers=headers,
    )
    assert list_resp.json()["data"] == []


@pytest.mark.asyncio
async def test_delete_nonexistent_relationship_returns_404(
    client: AsyncClient, db_session: AsyncSession
):
    """Deleting a relationship that does not exist returns 404."""
    user = await create_test_user(db_session, email="rel6@test.com")
    response = await client.delete(
        "/contact-relationships/99999",
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_other_users_relationship(
    client: AsyncClient, db_session: AsyncSession
):
    """User B cannot delete a relationship belonging to User A."""
    user_a = await create_test_user(db_session, email="relA@test.com")
    user_b = await create_test_user(db_session, email="relB@test.com")

    c1 = await create_test_contact(db_session, user_id=user_a.id, name="A1")
    c2 = await create_test_contact(db_session, user_id=user_a.id, name="A2")

    create_resp = await client.post(
        "/contact-relationships",
        json={"contact_id_1": c1.id, "contact_id_2": c2.id, "strength": 1.0},
        headers=make_auth_headers(user_a.id),
    )
    assert create_resp.status_code == 201
    rel_id = create_resp.json()["data"]["id"]

    # User B attempts to delete User A's relationship
    delete_resp = await client.delete(
        f"/contact-relationships/{rel_id}",
        headers=make_auth_headers(user_b.id),
    )
    assert delete_resp.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_list_other_users_relationships(
    client: AsyncClient, db_session: AsyncSession
):
    """User B cannot see User A's relationships by probing contact IDs."""
    user_a = await create_test_user(db_session, email="relC@test.com")
    user_b = await create_test_user(db_session, email="relD@test.com")

    c1 = await create_test_contact(db_session, user_id=user_a.id, name="A1")
    c2 = await create_test_contact(db_session, user_id=user_a.id, name="A2")

    await client.post(
        "/contact-relationships",
        json={"contact_id_1": c1.id, "contact_id_2": c2.id, "strength": 2.0},
        headers=make_auth_headers(user_a.id),
    )

    # User B lists relationships scoped by their own user_id — should see nothing
    response = await client.get(
        f"/contact-relationships/contacts/{c1.id}",
        headers=make_auth_headers(user_b.id),
    )
    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.asyncio
async def test_create_relationship_requires_auth(client: AsyncClient):
    """Unauthenticated POST is rejected with 401."""
    response = await client.post(
        "/contact-relationships",
        json={"contact_id_1": 1, "contact_id_2": 2, "strength": 1.0},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_relationships_requires_auth(client: AsyncClient):
    """Unauthenticated GET is rejected with 401."""
    response = await client.get("/contact-relationships/contacts/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_relationship_requires_auth(client: AsyncClient):
    """Unauthenticated DELETE is rejected with 401."""
    response = await client.delete("/contact-relationships/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upsert_updates_strength(client: AsyncClient, db_session: AsyncSession):
    """Creating a duplicate edge updates its strength (upsert semantics)."""
    user = await create_test_user(db_session, email="rel7@test.com")
    c1 = await create_test_contact(db_session, user_id=user.id, name="A")
    c2 = await create_test_contact(db_session, user_id=user.id, name="B")
    headers = make_auth_headers(user.id)

    await client.post(
        "/contact-relationships",
        json={"contact_id_1": c1.id, "contact_id_2": c2.id, "strength": 1.0},
        headers=headers,
    )
    resp2 = await client.post(
        "/contact-relationships",
        json={"contact_id_1": c1.id, "contact_id_2": c2.id, "strength": 5.0},
        headers=headers,
    )
    assert resp2.status_code == 201
    assert resp2.json()["data"]["strength"] == pytest.approx(5.0)

    # Still only one relationship
    list_resp = await client.get(
        f"/contact-relationships/contacts/{c1.id}",
        headers=headers,
    )
    assert len(list_resp.json()["data"]) == 1
