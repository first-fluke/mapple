from sqlalchemy.ext.asyncio import AsyncSession

from src.globe.repository import GlobeRepository
from src.globe.schemas import GlobeArcOut, GlobeDataOut, GlobePinOut


class GlobeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = GlobeRepository(session)

    async def get_globe_data(
        self, user_id: int, *, limit: int = 200
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

        # Arcs are empty for now — will be populated when communication
        # tracking is implemented. The bridge protocol supports them.
        arcs: list[GlobeArcOut] = []

        return GlobeDataOut(pins=pins, arcs=arcs)
