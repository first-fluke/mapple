from sqlalchemy.ext.asyncio import AsyncSession

from src.globe.repository import GlobeRepository
from src.globe.schemas import GlobeArcOut, GlobeDataOut, GlobePinOut


class GlobeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = GlobeRepository(session)

    async def get_globe_data(
        self, user_id: str, *, limit: int = 200
    ) -> GlobeDataOut:
        contacts = await self.repo.find_contacts_with_location(
            user_id, limit=limit
        )

        pins = [
            GlobePinOut(
                id=str(c.id),
                name=c.name,
                avatar_url=c.avatar_url or "",
                lat=c.latitude,  # type: ignore[arg-type]
                lng=c.longitude,  # type: ignore[arg-type]
            )
            for c in contacts
            if c.latitude is not None and c.longitude is not None
        ]

        arc_rows = await self.repo.find_relationship_arcs(user_id, limit=limit)

        # Normalize strength to 0..1 across the user's edges.
        # strength in DB is raw shared meeting count (always > 0 per constraint).
        max_strength = max((r.strength for r in arc_rows), default=0.0)

        arcs = [
            GlobeArcOut(
                id=row.rel_id,
                start_lat=row.lat_1,
                start_lng=row.lng_1,
                end_lat=row.lat_2,
                end_lng=row.lng_2,
                type="relationship",
                frequency=int(row.strength),
                strength=row.strength / max_strength if max_strength > 0 else 0.0,
                contact_ids=[str(row.contact_id_1), str(row.contact_id_2)],
                source_contact_id=row.contact_id_1,
                target_contact_id=row.contact_id_2,
                source_name=row.name_1,
                target_name=row.name_2,
            )
            for row in arc_rows
        ]

        return GlobeDataOut(pins=pins, arcs=arcs)
