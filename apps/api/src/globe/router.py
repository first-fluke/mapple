from fastapi import APIRouter, Depends, Header, Query, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.globe.schemas import BboxQuery, GlobeDataOut
from src.globe.service import GlobeService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse, AppException
from src.lib.redis import get_redis
from fastapi import APIRouter, Depends, Query
from src.globe.schemas import GlobeDataOut
from src.lib.exceptions import ApiResponse

router = APIRouter(prefix="/globe", tags=["globe"])


@router.get("/data")
async def get_globe_data(
    response: Response,
    bbox: str = Query(description="Bounding box: west,south,east,north"),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    if_none_match: str | None = Header(default=None),
) -> ApiResponse[GlobeDataOut]:
    try:
        parsed_bbox = BboxQuery.from_string(bbox)
    except (ValueError, IndexError) as e:
        raise AppException(
            status_code=400,
            code="INVALID_BBOX",
            message=str(e),
        ) from e

    service = GlobeService(session, redis)
    data, etag = await service.get_globe_data(user_id, parsed_bbox)

    if if_none_match and if_none_match.strip('"') == etag:
        response.status_code = 304
        return Response(status_code=304)  # type: ignore[return-value]

    response.headers["ETag"] = f'"{etag}"'
    response.headers["Cache-Control"] = "private, max-age=60"
    limit: int = Query(default=200, ge=1, le=500),
    """Return pins and arcs for the globe visualisation."""
    service = GlobeService(session)
    data = await service.get_globe_data(user_id, limit=limit)
    sw_lat: float = Query(..., ge=-90, le=90),
    sw_lng: float = Query(..., ge=-180, le=180),
    ne_lat: float = Query(..., ge=-90, le=90),
    ne_lng: float = Query(..., ge=-180, le=180),
    data = await service.get_data(user_id, sw_lat, sw_lng, ne_lat, ne_lng)
    return ApiResponse(data=data)
