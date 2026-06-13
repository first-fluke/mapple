from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contact_relationships.models import ContactRelationship
from src.contacts.models import Contact


@dataclass
class RelationshipArcRow:
    rel_id: int
    contact_id_1: int
    contact_id_2: int
    name_1: str
    name_2: str
    lat_1: float
    lng_1: float
    lat_2: float
    lng_2: float
    strength: float


class GlobeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_contacts_with_location(
        self, user_id: str, *, limit: int = 200
    ) -> list[Contact]:
        stmt = (
            select(Contact)
            .where(
                Contact.user_id == user_id,
                Contact.latitude.is_not(None),
                Contact.longitude.is_not(None),
            )
            .order_by(Contact.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_relationship_arcs(
        self, user_id: str, *, limit: int = 200
    ) -> list[RelationshipArcRow]:
        """Return relationship edges where both endpoints have lat/lng."""
        c1 = Contact.__table__.alias("c1")
        c2 = Contact.__table__.alias("c2")
        rel = ContactRelationship.__table__

        stmt = (
            select(
                rel.c.id.label("rel_id"),
                rel.c.contact_id_1,
                rel.c.contact_id_2,
                c1.c.name.label("name_1"),
                c2.c.name.label("name_2"),
                c1.c.latitude.label("lat_1"),
                c1.c.longitude.label("lng_1"),
                c2.c.latitude.label("lat_2"),
                c2.c.longitude.label("lng_2"),
                rel.c.strength,
            )
            .join(c1, rel.c.contact_id_1 == c1.c.id)
            .join(c2, rel.c.contact_id_2 == c2.c.id)
            .where(
                rel.c.user_id == user_id,
                c1.c.latitude.is_not(None),
                c1.c.longitude.is_not(None),
                c2.c.latitude.is_not(None),
                c2.c.longitude.is_not(None),
            )
            .order_by(rel.c.strength.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return [
            RelationshipArcRow(
                rel_id=row["rel_id"],
                contact_id_1=row["contact_id_1"],
                contact_id_2=row["contact_id_2"],
                name_1=row["name_1"],
                name_2=row["name_2"],
                lat_1=float(row["lat_1"]),
                lng_1=float(row["lng_1"]),
                lat_2=float(row["lat_2"]),
                lng_2=float(row["lng_2"]),
                strength=float(row["strength"]),
            )
            for row in rows
        ]
