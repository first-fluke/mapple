import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.experiences.models import Experience


class GlobeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_contacts_in_bbox(
        self,
        user_id: int,
        sw_lat: float,
        sw_lng: float,
        ne_lat: float,
        ne_lng: float,
    ) -> list[Contact]:
        stmt = (
            select(Contact)
            .where(
                Contact.user_id == user_id,
                Contact.lat.is_not(None),
                Contact.lng.is_not(None),
                Contact.lat >= sw_lat,
                Contact.lat <= ne_lat,
                Contact.lng >= sw_lng,
                Contact.lng <= ne_lng,
            )
            .order_by(Contact.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_shared_org_pairs(
        self, contact_ids: list[int]
    ) -> list[tuple[int, int, int]]:
        """Find pairs of contacts that share an organization.
        Returns list of (contact_a_id, contact_b_id, shared_org_count).
        """
        if len(contact_ids) < 2:
            return []

        e1 = sa.alias(Experience.__table__, name="e1")
        e2 = sa.alias(Experience.__table__, name="e2")

        stmt = (
            select(
                e1.c.contact_id.label("contact_a"),
                e2.c.contact_id.label("contact_b"),
                sa.func.count().label("shared_count"),
            )
            .select_from(e1.join(e2, e1.c.organization_id == e2.c.organization_id))
            .where(
                e1.c.contact_id.in_(contact_ids),
                e2.c.contact_id.in_(contact_ids),
                e1.c.contact_id < e2.c.contact_id,
            )
            .group_by(e1.c.contact_id, e2.c.contact_id)
        )
        result = await self.session.execute(stmt)
        return [(row.contact_a, row.contact_b, row.shared_count) for row in result]
