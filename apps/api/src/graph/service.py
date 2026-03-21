import json

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.graph.repository import GraphRepository
from src.graph.schemas import ClusterOut, EdgeOut, EdgeType

CACHE_TTL_SECONDS = 300

# Organization-backed types use the experience table
_ORG_TYPES = {EdgeType.COMPANY, EdgeType.SCHOOL}


class GraphService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.repo = GraphRepository(session)
        self.redis = redis

    async def get_edges(self, edge_type: EdgeType) -> list[EdgeOut]:
        cache_key = f"graph:edges:{edge_type}"
        cached = await self.redis.get(cache_key)
        if cached:
            return [EdgeOut.model_validate(e) for e in json.loads(cached)]

        if edge_type not in _ORG_TYPES:
            return []

        rows = await self.repo.find_edges_by_org_type(edge_type.value)
        edges = [
            EdgeOut(
                source_contact_id=row["source_contact_id"],
                target_contact_id=row["target_contact_id"],
                type=edge_type,
                label=row["label"],
            )
            for row in rows
        ]
        await self.redis.set(
            cache_key,
            json.dumps([e.model_dump(mode="json") for e in edges]),
            ex=CACHE_TTL_SECONDS,
        )
        return edges

    async def get_clusters(self, edge_type: EdgeType) -> list[ClusterOut]:
        cache_key = f"graph:clusters:{edge_type}"
        cached = await self.redis.get(cache_key)
        if cached:
            return [ClusterOut.model_validate(c) for c in json.loads(cached)]

        if edge_type not in _ORG_TYPES:
            return []

        rows = await self.repo.find_clusters_by_org_type(edge_type.value)
        clusters = [
            ClusterOut(
                id=row["id"],
                type=edge_type,
                label=row["label"],
                contact_ids=row["contact_ids"],
            )
            for row in rows
        ]
        await self.redis.set(
            cache_key,
            json.dumps([c.model_dump(mode="json") for c in clusters]),
            ex=CACHE_TTL_SECONDS,
        )
        return clusters
