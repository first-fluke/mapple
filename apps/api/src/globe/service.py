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
