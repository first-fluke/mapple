import json

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.graph.repository import GraphRepository
from src.graph.schemas import (
    ClusterOut,
    EdgeOut,
    EdgeType,
    GraphDataOut,
    GraphLinkOut,
    GraphNodeOut,
    LinkType,
)

CACHE_TTL_SECONDS = 300

# Organization-backed types use the experience table
_ORG_TYPES = {EdgeType.COMPANY, EdgeType.SCHOOL}

# Maps raw org type string to force-graph LinkType
_ORG_TYPE_TO_LINK_TYPE: dict[str, LinkType] = {
    "company": LinkType.COLLEAGUE,
    "school": LinkType.CLASSMATE,
}


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

    async def get_graph_data(
        self,
        user_id: str,
        *,
        search: str | None = None,
        link_type: LinkType | None = None,
    ) -> GraphDataOut:
        """Build force-graph nodes + links for the authenticated user.

        Nodes  = the user's contacts (optionally filtered by name search).
        Links  = contact_relationship rows among those contacts, with LinkType
                 derived from shared organization type:
                   company  → colleague
                   school   → classmate
                   (other)  → other
                   (none)   → friend

        Both results are cached per-user for CACHE_TTL_SECONDS.
        The cache key encodes search + link_type so different filter
        combinations stay isolated.
        """
        cache_key = f"graph:data:{user_id}:s={search or ''}:t={link_type or ''}"
        cached = await self.redis.get(cache_key)
        if cached:
            return GraphDataOut.model_validate(json.loads(cached))

        contact_rows = await self.repo.find_graph_contacts(user_id, search=search)
        contact_id_set = {c.id for c in contact_rows}

        nodes = [
            GraphNodeOut(id=str(c.id), name=c.name, avatar_url=c.avatar_url)
            for c in contact_rows
        ]

        link_rows = await self.repo.find_graph_links(
            user_id,
            contact_ids=list(contact_id_set),
        )

        links: list[GraphLinkOut] = []
        for row in link_rows:
            # Derive LinkType from the shared org type
            if row.org_type is not None:
                ltype = _ORG_TYPE_TO_LINK_TYPE.get(row.org_type, LinkType.OTHER)
                label = row.label  # shared org name
            else:
                ltype = LinkType.FRIEND
                label = None  # no shared org; omit label

            if link_type is not None and ltype != link_type:
                continue

            links.append(
                GraphLinkOut(
                    source=str(row.contact_id_1),
                    target=str(row.contact_id_2),
                    type=ltype,
                    label=label,
                )
            )

        result = GraphDataOut(nodes=nodes, links=links)
        await self.redis.set(
            cache_key,
            json.dumps(result.model_dump(mode="json")),
            ex=CACHE_TTL_SECONDS,
        )
        return result

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
