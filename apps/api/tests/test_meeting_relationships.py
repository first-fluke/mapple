"""Regression tests: meeting attendee changes drive relationship strength.

The relationship strength service (ContactRelationshipService) computes edge
strength from the number of shared meetings between two contacts. These tests
verify it is actually wired into the meeting create / update / delete flow, so
the globe arcs reflect real meeting history — not only manually-created edges.
"""

import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_test_contact, create_test_user, make_auth_headers

_WHEN = datetime.datetime(2026, 1, 1, 10, 0, 0).isoformat()


async def _strength(db_session: AsyncSession, user_id: str, a: int, b: int) -> float | None:
    c1, c2 = sorted([a, b])
    row = await db_session.execute(
        text(
            "SELECT strength FROM contact_relationship "
            "WHERE user_id = :uid AND contact_id_1 = :c1 AND contact_id_2 = :c2"
        ),
        {"uid": user_id, "c1": c1, "c2": c2},
    )
    val = row.scalar_one_or_none()
    return float(val) if val is not None else None


@pytest.mark.asyncio
async def test_creating_meeting_creates_relationship(
    client: AsyncClient, db_session: AsyncSession
):
    user = await create_test_user(db_session, email="mr1@test.com")
    a = await create_test_contact(db_session, user_id=user.id, name="A")
    b = await create_test_contact(db_session, user_id=user.id, name="B")

    resp = await client.post(
        "/meetings",
        json={"title": "Coffee", "starts_at": _WHEN, "attendee_contact_ids": [a.id, b.id]},
        headers=make_auth_headers(user.id),
    )
    assert resp.status_code == 201

    # One shared meeting → strength 1.
    assert await _strength(db_session, user.id, a.id, b.id) == 1.0


@pytest.mark.asyncio
async def test_two_meetings_increase_strength(
    client: AsyncClient, db_session: AsyncSession
):
    user = await create_test_user(db_session, email="mr2@test.com")
    a = await create_test_contact(db_session, user_id=user.id, name="A")
    b = await create_test_contact(db_session, user_id=user.id, name="B")
    headers = make_auth_headers(user.id)

    for title in ("M1", "M2"):
        resp = await client.post(
            "/meetings",
            json={"title": title, "starts_at": _WHEN, "attendee_contact_ids": [a.id, b.id]},
            headers=headers,
        )
        assert resp.status_code == 201

    # Two shared meetings → strength 2.
    assert await _strength(db_session, user.id, a.id, b.id) == 2.0


@pytest.mark.asyncio
async def test_deleting_meeting_removes_relationship(
    client: AsyncClient, db_session: AsyncSession
):
    user = await create_test_user(db_session, email="mr3@test.com")
    a = await create_test_contact(db_session, user_id=user.id, name="A")
    b = await create_test_contact(db_session, user_id=user.id, name="B")
    headers = make_auth_headers(user.id)

    created = await client.post(
        "/meetings",
        json={"title": "Solo shared", "starts_at": _WHEN, "attendee_contact_ids": [a.id, b.id]},
        headers=headers,
    )
    meeting_id = created.json()["data"]["id"]
    assert await _strength(db_session, user.id, a.id, b.id) == 1.0

    resp = await client.delete(f"/meetings/{meeting_id}", headers=headers)
    assert resp.status_code == 204

    # The only shared meeting is gone → relationship removed.
    assert await _strength(db_session, user.id, a.id, b.id) is None


@pytest.mark.asyncio
async def test_updating_attendees_recomputes_relationships(
    client: AsyncClient, db_session: AsyncSession
):
    user = await create_test_user(db_session, email="mr4@test.com")
    a = await create_test_contact(db_session, user_id=user.id, name="A")
    b = await create_test_contact(db_session, user_id=user.id, name="B")
    c = await create_test_contact(db_session, user_id=user.id, name="C")
    headers = make_auth_headers(user.id)

    created = await client.post(
        "/meetings",
        json={"title": "Trio", "starts_at": _WHEN, "attendee_contact_ids": [a.id, b.id, c.id]},
        headers=headers,
    )
    meeting_id = created.json()["data"]["id"]
    assert await _strength(db_session, user.id, a.id, c.id) == 1.0
    assert await _strength(db_session, user.id, b.id, c.id) == 1.0

    # Drop C from the meeting → its edges should disappear, A-B remains.
    resp = await client.put(
        f"/meetings/{meeting_id}",
        json={"attendee_contact_ids": [a.id, b.id]},
        headers=headers,
    )
    assert resp.status_code == 200

    assert await _strength(db_session, user.id, a.id, b.id) == 1.0
    assert await _strength(db_session, user.id, a.id, c.id) is None
    assert await _strength(db_session, user.id, b.id, c.id) is None
