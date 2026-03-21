import hashlib
import json

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.globe.repository import GlobeRepository
from src.globe.schemas import (
    BboxQuery,
    GlobeClusterOut,
    GlobeContactOut,
    GlobeDataOut,
    GlobeRelationshipOut,
)

CACHE_TTL = 300  # 5 minutes
CACHE_PREFIX = "globe:data"


class GlobeService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.repo = GlobeRepository(session)
        self.redis = redis

    def _cache_key(self, user_id: int, bbox: BboxQuery) -> str:
        bbox_str = f"{bbox.west},{bbox.south},{bbox.east},{bbox.north}"
        return f"{CACHE_PREFIX}:{user_id}:{bbox_str}"

    def _compute_etag(self, data: dict) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(raw.encode()).hexdigest()  # noqa: S324

    async def get_globe_data(
        self,
        user_id: int,
        bbox: BboxQuery,
    ) -> tuple[GlobeDataOut, str]:
        cache_key = self._cache_key(user_id, bbox)

        # Try cache
        cached = await self.redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            etag = self._compute_etag(data)
            return GlobeDataOut(**data), etag

        # Query database
        contacts, relationships, clusters = await self._fetch_data(user_id, bbox)

        result = GlobeDataOut(
            contacts=contacts,
            relationships=relationships,
            clusters=clusters,
        )

        data = result.model_dump(mode="json")
        etag = self._compute_etag(data)

        # Cache result
        await self.redis.set(cache_key, json.dumps(data, default=str), ex=CACHE_TTL)

        return result, etag

    async def _fetch_data(
        self,
        user_id: int,
        bbox: BboxQuery,
    ) -> tuple[list[GlobeContactOut], list[GlobeRelationshipOut], list[GlobeClusterOut]]:
        raw_contacts = await self.repo.find_contacts_in_bbox(user_id, bbox)
        contacts = [GlobeContactOut(**c) for c in raw_contacts]

        raw_relationships = await self.repo.find_relationships_in_bbox(user_id, bbox)
        relationships = [GlobeRelationshipOut(**r) for r in raw_relationships]

        raw_clusters = await self.repo.find_clusters_in_bbox(user_id, bbox)
        clusters = [GlobeClusterOut(**c) for c in raw_clusters]

        return contacts, relationships, clusters

    @staticmethod
    async def invalidate_user_cache(redis: Redis, user_id: int) -> None:
        pattern = f"{CACHE_PREFIX}:{user_id}:*"
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break
from src.globe.schemas import GlobeArcOut, GlobeDataOut, GlobePinOut
from src.contacts.models import Contact
from src.globe.schemas import GlobeArcOut, GlobeClusterOut, GlobeDataOut, GlobePinOut
CLUSTER_THRESHOLD = 200
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self, user_id: int, *, limit: int = 200
    ) -> GlobeDataOut:
        contacts = await self.repo.find_contacts_with_location(
            user_id, limit=limit
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
    async def get_data(
        sw_lat: float,
        sw_lng: float,
        ne_lat: float,
        ne_lng: float,
        contacts = await self.repo.find_contacts_in_bbox(
            user_id, sw_lat, sw_lng, ne_lat, ne_lng
        if len(contacts) > CLUSTER_THRESHOLD:
            pins, clusters = self._cluster_contacts(
                contacts, sw_lat, sw_lng, ne_lat, ne_lng
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
        return GlobeDataOut(pins=pins, arcs=arcs, clusters=clusters)
    def _cluster_contacts(
        contacts: list[Contact],
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
            else:
                avg_lat = sum(c.lat for c in group if c.lat) / len(group)
                avg_lng = sum(c.lng for c in group if c.lng) / len(group)
                clusters.append(
                    GlobeClusterOut(
                        lat=avg_lat,
                        lng=avg_lng,
                        count=len(group),
                        contact_ids=[str(c.id) for c in group],
        return pins, clusters
