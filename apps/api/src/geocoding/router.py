import httpx
from fastapi import APIRouter, Depends, Query

from src.lib.auth import get_current_user_id
from src.lib.exceptions import ApiResponse, AppException

router = APIRouter(prefix="/geocoding", tags=["geocoding"])


@router.get("/reverse")
async def reverse_geocode(
    lat: float = Query(...),
    lng: float = Query(...),
    _user_id: str = Depends(get_current_user_id),
) -> ApiResponse[dict]:
    """Reverse geocode coordinates to country and city using Nominatim."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lng,
                "format": "json",
                "accept-language": "en",
                "zoom": 10,
            },
            headers={"User-Agent": "GlobeCRM/0.1"},
            timeout=10.0,
        )
        if response.status_code != 200:
            raise AppException(
                status_code=502,
                code="GEOCODING_ERROR",
                message="Failed to reverse geocode coordinates",
            )
        data = response.json()
        address = data.get("address", {})
        country = address.get("country")
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("state")
        )
        return ApiResponse(
            data={
                "country": country,
                "city": city,
                "display_name": data.get("display_name"),
            }
        )
