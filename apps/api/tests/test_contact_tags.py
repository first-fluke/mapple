"""Regression tests for ContactTag FK design (contact_id + tag_id composite PK).

These tests exercise the full repository/service/router stack with real Tag rows,
proving that the ORM model matches the migrated schema (no id/name columns on
contact_tag) and that contact.tags yields Tag objects correctly.

The drift that caused the 500 errors was:
  - ORM ContactTag had id (PK), name, created_at  (inline-string design)
  - Real DB contact_tag has composite PK (contact_id, tag_id), color, updated_at

Every test here fails if the old model is present, and passes with the fixed model.
"""

import pytest

from tests.conftest import (
    create_test_contact,
    create_test_tag,
    create_test_user,
    make_auth_headers,
)


# ---------------------------------------------------------------------------
# Repository-level FK regression
# ---------------------------------------------------------------------------


async def test_contact_create_with_tag_ids_via_repository(db_session):
    """Creating a contact with tag_ids inserts rows into contact_tag with composite PK.

    This test hits the repository directly and would fail with the old model
    (ContactTag.id, ContactTag.name) because the DB schema has no such columns.
    """
    from src.contacts.repository import ContactRepository

    user = await create_test_user(db_session, email="repo-tag@test.com")
    tag = await create_test_tag(db_session, user_id=user.id, name="vip")

    repo = ContactRepository(db_session)
    contact = await repo.create(
        user_id=user.id,
        name="Tagged Contact",
        email=None,
        phone=None,
        tag_ids=[tag.id],
    )

    assert len(contact.tags) == 1
    assert contact.tags[0].id == tag.id
    assert contact.tags[0].name == "vip"


async def test_contact_update_replaces_tags_via_repository(db_session):
    """Updating a contact's tag_ids replaces the M2M association correctly."""
    from src.contacts.repository import ContactRepository

    user = await create_test_user(db_session, email="repo-update-tag@test.com")
    tag_a = await create_test_tag(db_session, user_id=user.id, name="old-tag")
    tag_b = await create_test_tag(db_session, user_id=user.id, name="new-tag")

    repo = ContactRepository(db_session)
    contact = await repo.create(
        user_id=user.id,
        name="Swap Tags Contact",
        email=None,
        phone=None,
        tag_ids=[tag_a.id],
    )
    assert len(contact.tags) == 1
    assert contact.tags[0].name == "old-tag"

    updated = await repo.update(contact, user_id=user.id, tag_ids=[tag_b.id])
    assert len(updated.tags) == 1
    assert updated.tags[0].name == "new-tag"


async def test_contact_create_ignores_foreign_user_tag_ids(db_session):
    """tag_ids belonging to a different user are silently ignored (ownership scoping)."""
    from src.contacts.repository import ContactRepository

    user_a = await create_test_user(db_session, email="owner@test.com")
    user_b = await create_test_user(db_session, email="other@test.com")
    other_tag = await create_test_tag(db_session, user_id=user_b.id, name="other-tag")

    repo = ContactRepository(db_session)
    contact = await repo.create(
        user_id=user_a.id,
        name="No Foreign Tags",
        email=None,
        phone=None,
        tag_ids=[other_tag.id],
    )

    # other_tag is not owned by user_a — must not be associated
    assert contact.tags == []


# ---------------------------------------------------------------------------
# HTTP layer regression (proves the 500 is gone on GET /contacts/{id})
# ---------------------------------------------------------------------------


async def test_get_contact_with_tags_returns_tag_list(client, db_session):
    """GET /contacts/{id} must return tags as [{id, name}] not 500.

    This is the primary regression: the selectin load of contact.tags
    against the real DB schema (composite PK, no id column on contact_tag)
    previously crashed with 'column contact_tag.id does not exist'.
    """
    user = await create_test_user(db_session, email="get-tagged@test.com")
    tag = await create_test_tag(db_session, user_id=user.id, name="friend")

    # Create contact with tag via API
    headers = make_auth_headers(user.id)
    create_resp = await client.post(
        "/contacts",
        json={"name": "Tagged Person", "tag_ids": [tag.id]},
        headers=headers,
    )
    assert create_resp.status_code == 201, create_resp.text
    contact_id = create_resp.json()["data"]["id"]

    # Fetch via GET — this is the endpoint that 500'd before the fix
    get_resp = await client.get(f"/contacts/{contact_id}", headers=headers)
    assert get_resp.status_code == 200, get_resp.text
    data = get_resp.json()["data"]
    assert data["tags"] == [{"id": tag.id, "name": "friend"}]


async def test_list_contacts_with_tags_does_not_500(client, db_session):
    """GET /contacts must not 500 when contacts have associated tags."""
    user = await create_test_user(db_session, email="list-tagged@test.com")
    tag = await create_test_tag(db_session, user_id=user.id, name="colleague")

    headers = make_auth_headers(user.id)
    resp = await client.post(
        "/contacts",
        json={"name": "Another Tagged Person", "tag_ids": [tag.id]},
        headers=headers,
    )
    assert resp.status_code == 201

    list_resp = await client.get("/contacts", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    contacts = list_resp.json()["data"]
    assert len(contacts) == 1
    assert contacts[0]["tags"] == [{"id": tag.id, "name": "colleague"}]


async def test_filter_contacts_by_tag_name(client, db_session):
    """GET /contacts?tag=<name> filters by tag name via the FK join (not ContactTag.name)."""
    user = await create_test_user(db_session, email="filter-tag@test.com")
    vip_tag = await create_test_tag(db_session, user_id=user.id, name="vip")

    headers = make_auth_headers(user.id)
    # Create one tagged, one untagged
    await client.post(
        "/contacts", json={"name": "VIP Person", "tag_ids": [vip_tag.id]}, headers=headers
    )
    await client.post(
        "/contacts", json={"name": "Regular Person", "tag_ids": []}, headers=headers
    )

    # Filter by tag name
    resp = await client.get("/contacts", params={"tag": "vip"}, headers=headers)
    assert resp.status_code == 200, resp.text
    contacts = resp.json()["data"]
    assert len(contacts) == 1
    assert contacts[0]["name"] == "VIP Person"


async def test_patch_contact_tag_ids_replaces_association(client, db_session):
    """PATCH /contacts/{id} with tag_ids replaces the contact's tags."""
    user = await create_test_user(db_session, email="patch-tag@test.com")
    tag_a = await create_test_tag(db_session, user_id=user.id, name="alpha")
    tag_b = await create_test_tag(db_session, user_id=user.id, name="beta")

    headers = make_auth_headers(user.id)
    create_resp = await client.post(
        "/contacts",
        json={"name": "Patch Tags Contact", "tag_ids": [tag_a.id]},
        headers=headers,
    )
    assert create_resp.status_code == 201
    contact_id = create_resp.json()["data"]["id"]

    patch_resp = await client.patch(
        f"/contacts/{contact_id}",
        json={"tag_ids": [tag_b.id]},
        headers=headers,
    )
    assert patch_resp.status_code == 200, patch_resp.text
    tags = patch_resp.json()["data"]["tags"]
    assert len(tags) == 1
    assert tags[0]["name"] == "beta"


async def test_contact_without_tags_returns_empty_list(client, db_session):
    """A contact created without tag_ids returns tags: [] (not error)."""
    user = await create_test_user(db_session, email="no-tags@test.com")
    headers = make_auth_headers(user.id)

    resp = await client.post(
        "/contacts", json={"name": "No Tags Contact"}, headers=headers
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["tags"] == []
