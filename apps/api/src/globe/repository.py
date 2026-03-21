from geoalchemy2.functions import ST_X, ST_Y, ST_MakeEnvelope, ST_SnapToGrid, ST_Within
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.experiences.models import Experience
from src.globe.schemas import BboxQuery
from src.organizations.models import Organization


class GlobeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_contacts_in_bbox(
        self,
        user_id: int,
        bbox: BboxQuery,
    ) -> list[dict]:
        envelope = ST_MakeEnvelope(bbox.west, bbox.south, bbox.east, bbox.north, 4326)
        stmt = (
            select(
                Contact.id,
                Contact.name,
                Contact.email,
                Contact.phone,
                ST_Y(Contact.location).label("latitude"),
                ST_X(Contact.location).label("longitude"),
                Contact.created_at,
            )
            .where(
                Contact.user_id == user_id,
                Contact.location.is_not(None),
                ST_Within(Contact.location, envelope),
            )
            .order_by(Contact.id)
        )
        result = await self.session.execute(stmt)
        return [row._asdict() for row in result.all()]

    async def find_relationships_in_bbox(
        self,
        user_id: int,
        bbox: BboxQuery,
    ) -> list[dict]:
        envelope = ST_MakeEnvelope(bbox.west, bbox.south, bbox.east, bbox.north, 4326)

        # Contacts visible in the bbox
        visible = (
            select(Contact.id)
            .where(
                Contact.user_id == user_id,
                Contact.location.is_not(None),
                ST_Within(Contact.location, envelope),
            )
            .subquery()
        )

        # Find pairs of contacts sharing an organization
        e1 = Experience.__table__.alias("e1")
        e2 = Experience.__table__.alias("e2")
        stmt = (
            select(
                e1.c.contact_id.label("source_contact_id"),
                e2.c.contact_id.label("target_contact_id"),
                e1.c.organization_id,
                Organization.name.label("organization_name"),
            )
            .select_from(e1)
            .join(e2, (e1.c.organization_id == e2.c.organization_id) & (e1.c.contact_id < e2.c.contact_id))
            .join(Organization, Organization.id == e1.c.organization_id)
            .where(
                e1.c.contact_id.in_(select(visible.c.id)),
                e2.c.contact_id.in_(select(visible.c.id)),
            )
            .order_by(e1.c.contact_id, e2.c.contact_id)
        )
        result = await self.session.execute(stmt)
        return [row._asdict() for row in result.all()]

    async def find_clusters_in_bbox(
        self,
        user_id: int,
        bbox: BboxQuery,
        *,
        grid_size: float = 5.0,
    ) -> list[dict]:
        envelope = ST_MakeEnvelope(bbox.west, bbox.south, bbox.east, bbox.north, 4326)
        snapped = ST_SnapToGrid(Contact.location, grid_size)

        stmt = (
            select(
                ST_Y(snapped).label("latitude"),
                ST_X(snapped).label("longitude"),
                func.count(Contact.id).label("count"),
                func.array_agg(Contact.id).label("contact_ids"),
            )
            .where(
                Contact.user_id == user_id,
                Contact.location.is_not(None),
                ST_Within(Contact.location, envelope),
            )
            .group_by(snapped)
            .having(func.count(Contact.id) > 1)
            .order_by(func.count(Contact.id).desc())
        )
        result = await self.session.execute(stmt)
        return [row._asdict() for row in result.all()]

    async def get_user_data_version(self, user_id: int) -> str | None:
        """Get the latest updated_at across contacts for ETag computation."""
        stmt = select(func.max(Contact.updated_at)).where(Contact.user_id == user_id)
        result = await self.session.execute(stmt)
        ts = result.scalar_one_or_none()
        if ts is None:
            return None
        return str(int(ts.timestamp()))
