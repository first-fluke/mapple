from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.globe.schemas import GlobeDataOut
from src.globe.service import GlobeService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse

router = APIRouter(prefix="/globe", tags=["globe"])


@router.get("/data")
async def get_globe_data(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=200, ge=1, le=500),
) -> ApiResponse[GlobeDataOut]:
    """Return pins and arcs for the globe visualisation."""
    service = GlobeService(session)
    data = await service.get_globe_data(user_id, limit=limit)
    sw_lat: float = Query(..., ge=-90, le=90),
    sw_lng: float = Query(..., ge=-180, le=180),
    ne_lat: float = Query(..., ge=-90, le=90),
    ne_lng: float = Query(..., ge=-180, le=180),
    data = await service.get_data(user_id, sw_lat, sw_lng, ne_lat, ne_lng)
    return ApiResponse(data=data)
