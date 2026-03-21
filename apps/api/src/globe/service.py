from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.globe.repository import GlobeRepository
from src.globe.schemas import GlobeArcOut, GlobeClusterOut, GlobeDataOut, GlobePinOut

CLUSTER_THRESHOLD = 200


class GlobeService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = GlobeRepository(session)

    async def get_data(
        self,
        user_id: int,
        sw_lat: float,
        sw_lng: float,
        ne_lat: float,
        ne_lng: float,
    ) -> GlobeDataOut:
        contacts = await self.repo.find_contacts_in_bbox(
            user_id, sw_lat, sw_lng, ne_lat, ne_lng
        )

        if len(contacts) > CLUSTER_THRESHOLD:
            pins, clusters = self._cluster_contacts(
                contacts, sw_lat, sw_lng, ne_lat, ne_lng
            )
        else:
            pins = [
                GlobePinOut(
                    id=str(c.id),
                    name=c.name,
                    avatar_url=c.avatar_url,
                    lat=c.lat,
                    lng=c.lng,
                )
                for c in contacts
                if c.lat is not None and c.lng is not None
            ]
            clusters = []

        # Build arcs from shared organizations
        contact_ids = [c.id for c in contacts]
        contact_map = {c.id: c for c in contacts}
        pairs = await self.repo.find_shared_org_pairs(contact_ids)

        arcs = []
        for contact_a_id, contact_b_id, count in pairs:
            a = contact_map.get(contact_a_id)
            b = contact_map.get(contact_b_id)
            if a and b and a.lat and a.lng and b.lat and b.lng:
                arcs.append(
                    GlobeArcOut(
                        id=f"{a.id}-{b.id}",
                        start_lat=a.lat,
                        start_lng=a.lng,
                        end_lat=b.lat,
                        end_lng=b.lng,
                        type="meeting",
                        frequency=count,
                    )
                )

        return GlobeDataOut(pins=pins, arcs=arcs, clusters=clusters)

    def _cluster_contacts(
        self,
        contacts: list[Contact],
        sw_lat: float,
        sw_lng: float,
        ne_lat: float,
        ne_lng: float,
    ) -> tuple[list[GlobePinOut], list[GlobeClusterOut]]:
        """Grid-based clustering: split bbox into ~10x10 grid cells."""
        grid_size = 10
        lat_step = (ne_lat - sw_lat) / grid_size
        lng_step = (ne_lng - sw_lng) / grid_size

        cells: dict[tuple[int, int], list[Contact]] = {}
        for c in contacts:
            if c.lat is None or c.lng is None:
                continue
            row = min(int((c.lat - sw_lat) / lat_step), grid_size - 1) if lat_step > 0 else 0
            col = min(int((c.lng - sw_lng) / lng_step), grid_size - 1) if lng_step > 0 else 0
            cells.setdefault((row, col), []).append(c)

        pins: list[GlobePinOut] = []
        clusters: list[GlobeClusterOut] = []

        for _cell_key, group in cells.items():
            if len(group) == 1:
                c = group[0]
                pins.append(
                    GlobePinOut(
                        id=str(c.id),
                        name=c.name,
                        avatar_url=c.avatar_url,
                        lat=c.lat,
                        lng=c.lng,
                    )
                )
            else:
                avg_lat = sum(c.lat for c in group if c.lat) / len(group)
                avg_lng = sum(c.lng for c in group if c.lng) / len(group)
                clusters.append(
                    GlobeClusterOut(
                        lat=avg_lat,
                        lng=avg_lng,
                        count=len(group),
                        contact_ids=[str(c.id) for c in group],
                    )
                )

        return pins, clusters
