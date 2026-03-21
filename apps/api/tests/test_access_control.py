"""Security tests for cross-user access control (IDOR / Broken Access Control).

Covers OWASP A01 (Broken Access Control) with focus on:
- User-scoped resource isolation (contacts, experiences)
- Insecure Direct Object Reference (IDOR) prevention
- Horizontal privilege escalation
"""

import pytest

from tests.conftest import (
    create_test_contact,
    create_test_experience,
    create_test_organization,
    create_test_user,
    make_auth_headers,
)


async def _setup_two_users_with_data(db_session):
    """Create two users, each with their own contact and experience."""
    user_a = await create_test_user(
        db_session, provider_id="a-123", email="alice@test.com"
    )
    user_b = await create_test_user(
        db_session, provider_id="b-456", email="bob@test.com"
    )
    org = await create_test_organization(db_session)
    contact_a = await create_test_contact(
        db_session, user_id=user_a.id, name="Alice Contact"
    )
    contact_b = await create_test_contact(
        db_session, user_id=user_b.id, name="Bob Contact"
    )
    exp_a = await create_test_experience(
        db_session,
        contact_id=contact_a.id,
        organization_id=org.id,
        role="Alice Role",
    )
    exp_b = await create_test_experience(
        db_session,
        contact_id=contact_b.id,
        organization_id=org.id,
        role="Bob Role",
    )
    return user_a, user_b, contact_a, contact_b, exp_a, exp_b, org


# --- Cross-user experience access (IDOR) ---


@pytest.mark.xfail(
    strict=True,
    reason="CRITICAL: No authorization check — user can list any contact's experiences",
)
async def test_user_cannot_list_other_users_contact_experiences(client, db_session):
    """User B must NOT be able to list User A's contact's experiences."""
    user_a, user_b, contact_a, *_ = await _setup_two_users_with_data(db_session)

    response = await client.get(
        f"/contacts/{contact_a.id}/experiences",
        headers=make_auth_headers(user_b.id),
    )
    assert response.status_code in (403, 404)


@pytest.mark.xfail(
    strict=True,
    reason="CRITICAL: No authorization check — user can create experiences on any contact",
)
async def test_user_cannot_create_experience_on_others_contact(client, db_session):
    """User B must NOT be able to create an experience on User A's contact."""
    user_a, user_b, contact_a, _, _, _, org = await _setup_two_users_with_data(
        db_session
    )

    response = await client.post(
        f"/contacts/{contact_a.id}/experiences",
        json={"organization_id": org.id, "role": "Hacker"},
        headers=make_auth_headers(user_b.id),
    )
    assert response.status_code in (403, 404)


@pytest.mark.xfail(
    strict=True,
    reason="CRITICAL: No authorization check — user can update any contact's experience",
)
async def test_user_cannot_update_others_contact_experience(client, db_session):
    """User B must NOT be able to update User A's contact's experience."""
    user_a, user_b, contact_a, _, exp_a, _, org = await _setup_two_users_with_data(
        db_session
    )

    response = await client.put(
        f"/contacts/{contact_a.id}/experiences/{exp_a.id}",
        json={"role": "Pwned"},
        headers=make_auth_headers(user_b.id),
    )
    assert response.status_code in (403, 404)


@pytest.mark.xfail(
    strict=True,
    reason="CRITICAL: No authorization check — user can delete any contact's experience",
)
async def test_user_cannot_delete_others_contact_experience(client, db_session):
    """User B must NOT be able to delete User A's contact's experience."""
    user_a, user_b, contact_a, _, exp_a, _, _ = await _setup_two_users_with_data(
        db_session
    )

    response = await client.delete(
        f"/contacts/{contact_a.id}/experiences/{exp_a.id}",
        headers=make_auth_headers(user_b.id),
    )
    assert response.status_code in (403, 404)


# --- Legitimate access (positive tests) ---


async def test_user_can_list_own_contact_experiences(client, db_session):
    """User A must be able to list their own contact's experiences."""
    user_a, _, contact_a, _, exp_a, _, _ = await _setup_two_users_with_data(db_session)

    response = await client.get(
        f"/contacts/{contact_a.id}/experiences",
        headers=make_auth_headers(user_a.id),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["role"] == "Alice Role"


async def test_user_can_create_experience_on_own_contact(client, db_session):
    """User A must be able to create experiences on their own contact."""
    user_a, _, contact_a, _, _, _, org = await _setup_two_users_with_data(db_session)

    response = await client.post(
        f"/contacts/{contact_a.id}/experiences",
        json={"organization_id": org.id, "role": "New Role"},
        headers=make_auth_headers(user_a.id),
    )
    assert response.status_code == 201


async def test_nonexistent_contact_returns_404(client, db_session):
    """Accessing a non-existent contact must return 404."""
    user = await create_test_user(db_session)

    response = await client.get(
        "/contacts/99999/experiences",
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 404


async def test_me_returns_only_own_data(client, db_session):
    """GET /auth/me must return only the authenticated user's data."""
    user_a = await create_test_user(
        db_session, provider_id="me-a", email="a@test.com"
    )
    user_b = await create_test_user(
        db_session, provider_id="me-b", email="b@test.com"
    )

    # User A's token should return User A's data
    resp_a = await client.get("/auth/me", headers=make_auth_headers(user_a.id))
    assert resp_a.status_code == 200
    assert resp_a.json()["data"]["email"] == "a@test.com"

    # User B's token should return User B's data
    resp_b = await client.get("/auth/me", headers=make_auth_headers(user_b.id))
    assert resp_b.status_code == 200
    assert resp_b.json()["data"]["email"] == "b@test.com"


# --- IDOR via sequential IDs ---


async def test_contact_id_enumeration_risk(client, db_session):
    """Document that sequential integer IDs allow resource enumeration.

    An attacker can iterate contact IDs (1, 2, 3, ...) to discover
    and access other users' contacts. UUIDs would mitigate this.
    """
    user_a, user_b, contact_a, contact_b, _, _, _ = await _setup_two_users_with_data(
        db_session
    )

    # Sequential IDs are predictable
    assert abs(contact_a.id - contact_b.id) == 1

    # User B can probe sequential IDs to find User A's contacts
    # This is a design risk even if access control is fixed
    responses = []
    for cid in range(1, contact_b.id + 1):
        resp = await client.get(
            f"/contacts/{cid}/experiences",
            headers=make_auth_headers(user_b.id),
        )
        responses.append(resp.status_code)

    # Currently all return 200 (vulnerability), but even with access control,
    # 404 vs 403 response codes can leak existence of resources.
    # This test documents the enumeration risk.
    assert all(
        code in (200, 403, 404) for code in responses
    ), "Unexpected status codes during enumeration"
