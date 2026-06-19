from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.graph.schemas import ClusterOut, EdgeOut, EdgeType, GraphDataOut, LinkType
from src.graph.service import GraphService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.rate_limit import check_data_rate_limit
from src.lib.redis import get_redis

router = APIRouter(prefix="/graph", tags=["graph"], dependencies=[Depends(check_data_rate_limit)])


@router.get("/data")
async def get_graph_data(
    search: str | None = Query(default=None, description="Filter nodes by contact name (case-insensitive)"),
    type: LinkType | None = Query(
        default=None,
        description="Filter links by LinkType (colleague|classmate|friend|other)",
    ),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[GraphDataOut]:
    """Force-graph data for the authenticated user's contact network.

    Returns nodes (contacts) and links (relationships) shaped for the web
    force-graph component.  Both ``search`` and ``type`` are optional filters.
    """
    service = GraphService(session, redis)
    data = await service.get_graph_data(user_id, search=search, link_type=type)
    return ApiResponse(data=data)


@router.get("/edges")
async def list_edges(
    type: EdgeType = Query(..., description="Edge type filter"),
    _user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[list[EdgeOut]]:
    """List graph edges filtered by type."""
    service = GraphService(session, redis)
    edges = await service.get_edges(type)
    return ApiResponse(data=edges)


@router.get("/clusters")
async def list_clusters(
    type: EdgeType = Query(..., description="Cluster type filter"),
    _user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[list[ClusterOut]]:
    """List graph clusters filtered by type."""
    service = GraphService(session, redis)
    clusters = await service.get_clusters(type)
    return ApiResponse(data=clusters)
