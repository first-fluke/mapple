"""Regression tests for the globe data endpoint (Task A).

Covers:
- Arcs are returned for relationship edges where both contacts have coordinates.
- Edges where either endpoint lacks coordinates are excluded.
- Strength is normalized to 0..1.
- Arcs are scoped to the authenticated user.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_test_contact, create_test_user, make_auth_headers


async def _seed_relationship(
    db_session: AsyncSession,
    *,
    user_id: str,
    contact_id_1: int,
    contact_id_2: int,
    strength: float,
) -> None:
    c1, c2 = sorted([contact_id_1, contact_id_2])
    await db_session.execute(
        text(
            "INSERT INTO contact_relationship "
            "(user_id, contact_id_1, contact_id_2, strength) "
            "VALUES (:uid, :c1, :c2, :s)"
        ),
        {"uid": user_id, "c1": c1, "c2": c2, "s": strength},
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_globe_arcs_returned_for_located_contacts(
    client: AsyncClient, db_session: AsyncSession
):
    """Two located contacts with a relationship edge produce one arc."""
    user = await create_test_user(db_session, email="globe1@test.com")
    c1 = await create_test_contact(
        db_session, user_id=user.id, name="Alice", latitude=37.5665, longitude=126.978
    )
    c2 = await create_test_contact(
        db_session, user_id=user.id, name="Bob", latitude=35.6762, longitude=139.6503
    )
    await _seed_relationship(
        db_session,
        user_id=user.id,
        contact_id_1=c1.id,
        contact_id_2=c2.id,
        strength=3.0,
    )

    response = await client.get("/globe/data", headers=make_auth_headers(user.id))
    assert response.status_code == 200

    data = response.json()["data"]
    arcs = data["arcs"]
    assert len(arcs) == 1

    arc = arcs[0]
    # Coords must match ordered pair
    c_id_min = min(c1.id, c2.id)
    c_id_max = max(c1.id, c2.id)
    assert arc["source_contact_id"] == c_id_min
    assert arc["target_contact_id"] == c_id_max
    assert arc["frequency"] == 3
    # Single edge → normalized strength is 1.0
    assert arc["strength"] == pytest.approx(1.0)
    assert arc["type"] == "relationship"
    assert set(arc["contact_ids"]) == {str(c1.id), str(c2.id)}


@pytest.mark.asyncio
async def test_globe_arcs_correct_coordinates(
    client: AsyncClient, db_session: AsyncSession
):
    """Arc start/end coordinates match the contact lat/lng values."""
    user = await create_test_user(db_session, email="globe2@test.com")
    c1 = await create_test_contact(
        db_session, user_id=user.id, name="Seoul", latitude=37.5665, longitude=126.978
    )
    c2 = await create_test_contact(
        db_session, user_id=user.id, name="Tokyo", latitude=35.6762, longitude=139.6503
    )
    await _seed_relationship(
        db_session,
        user_id=user.id,
        contact_id_1=c1.id,
        contact_id_2=c2.id,
        strength=1.0,
    )

    response = await client.get("/globe/data", headers=make_auth_headers(user.id))
    assert response.status_code == 200

    arc = response.json()["data"]["arcs"][0]
    # The repository returns source = contact_id_1 (lower id)
    if c1.id < c2.id:
        assert arc["start_lat"] == pytest.approx(c1.latitude)
        assert arc["start_lng"] == pytest.approx(c1.longitude)
        assert arc["end_lat"] == pytest.approx(c2.latitude)
        assert arc["end_lng"] == pytest.approx(c2.longitude)
    else:
        assert arc["start_lat"] == pytest.approx(c2.latitude)
        assert arc["start_lng"] == pytest.approx(c2.longitude)
        assert arc["end_lat"] == pytest.approx(c1.latitude)
        assert arc["end_lng"] == pytest.approx(c1.longitude)


@pytest.mark.asyncio
async def test_globe_arcs_strength_normalized(
    client: AsyncClient, db_session: AsyncSession
):
    """Strength is normalized: the strongest edge == 1.0, weaker edges proportional."""
    user = await create_test_user(db_session, email="globe3@test.com")
    ca = await create_test_contact(
        db_session, user_id=user.id, name="A", latitude=0.0, longitude=0.0
    )
    cb = await create_test_contact(
        db_session, user_id=user.id, name="B", latitude=10.0, longitude=10.0
    )
    cc = await create_test_contact(
        db_session, user_id=user.id, name="C", latitude=20.0, longitude=20.0
    )
    # strength=2 for edge A-B, strength=4 for edge B-C
    await _seed_relationship(
        db_session, user_id=user.id,
        contact_id_1=ca.id, contact_id_2=cb.id, strength=2.0,
    )
    await _seed_relationship(
        db_session, user_id=user.id,
        contact_id_1=cb.id, contact_id_2=cc.id, strength=4.0,
    )

    response = await client.get("/globe/data", headers=make_auth_headers(user.id))
    assert response.status_code == 200

    arcs = response.json()["data"]["arcs"]
    assert len(arcs) == 2

    strengths = {arc["frequency"]: arc["strength"] for arc in arcs}
    assert strengths[4] == pytest.approx(1.0)       # max edge
    assert strengths[2] == pytest.approx(0.5)       # half of max


@pytest.mark.asyncio
async def test_globe_arcs_missing_coordinate_excluded(
    client: AsyncClient, db_session: AsyncSession
):
    """An edge where one contact has no location must be excluded from arcs."""
    user = await create_test_user(db_session, email="globe4@test.com")
    c_located = await create_test_contact(
        db_session, user_id=user.id, name="Located",
        latitude=37.5665, longitude=126.978,
    )
    c_no_loc = await create_test_contact(
        db_session, user_id=user.id, name="NoLocation",
        latitude=None, longitude=None,
    )
    await _seed_relationship(
        db_session, user_id=user.id,
        contact_id_1=c_located.id, contact_id_2=c_no_loc.id, strength=5.0,
    )

    response = await client.get("/globe/data", headers=make_auth_headers(user.id))
    assert response.status_code == 200

    arcs = response.json()["data"]["arcs"]
    assert arcs == [], f"Expected no arcs but got {arcs}"


@pytest.mark.asyncio
async def test_globe_arcs_scoped_to_user(
    client: AsyncClient, db_session: AsyncSession
):
    """A user only sees their own arcs, not another user's."""
    user_a = await create_test_user(db_session, email="globeA@test.com")
    user_b = await create_test_user(db_session, email="globeB@test.com")

    ca1 = await create_test_contact(
        db_session, user_id=user_a.id, name="A1", latitude=1.0, longitude=1.0
    )
    ca2 = await create_test_contact(
        db_session, user_id=user_a.id, name="A2", latitude=2.0, longitude=2.0
    )
    await _seed_relationship(
        db_session, user_id=user_a.id,
        contact_id_1=ca1.id, contact_id_2=ca2.id, strength=1.0,
    )

    # user_b has no relationships
    response = await client.get("/globe/data", headers=make_auth_headers(user_b.id))
    assert response.status_code == 200
    assert response.json()["data"]["arcs"] == []


@pytest.mark.asyncio
async def test_globe_data_requires_auth(client: AsyncClient):
    """The globe endpoint must reject unauthenticated requests."""
    response = await client.get("/globe/data")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_globe_no_arcs_when_no_relationships(
    client: AsyncClient, db_session: AsyncSession
):
    """Globe data returns empty arcs list when no relationships exist."""
    user = await create_test_user(db_session, email="globe5@test.com")
    await create_test_contact(
        db_session, user_id=user.id, name="Lonely", latitude=0.0, longitude=0.0
    )

    response = await client.get("/globe/data", headers=make_auth_headers(user.id))
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["arcs"] == []
    assert len(data["pins"]) == 1
