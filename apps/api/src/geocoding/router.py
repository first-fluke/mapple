"""Geocoding router — reverse geocode via Nominatim (OSM).

Enhancements:
- Redis-backed cache keyed by lat/lng rounded to 4 decimal places (TTL configurable,
  default 30 days).  4 decimal places gives ~11 m precision, safe for city/country.
- Polite max-1-req/s outbound limiter via asyncio.Semaphore + wall-clock check to
  respect the OSM Nominatim usage policy.
- Graceful failure: cache misses that result in Nominatim errors return 502 without
  crashing; cached hits are still served normally.
"""

import asyncio
import os
import time

import httpx
from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis

from src.lib.auth import get_current_user_id
from src.lib.exceptions import ApiResponse, AppException
from src.lib.rate_limit import check_data_rate_limit
from src.lib.redis import get_redis

GEOCODE_CACHE_TTL = int(os.getenv("GEOCODE_CACHE_TTL", str(30 * 24 * 3600)))  # 30 days default

router = APIRouter(prefix="/geocoding", tags=["geocoding"], dependencies=[Depends(check_data_rate_limit)])

# Semaphore: only one outbound Nominatim call at a time across all async workers.
_nominatim_sem = asyncio.Semaphore(1)
# Wall-clock timestamp of the last successful Nominatim HTTP call (module-level state).
_last_nominatim_call: float = 0.0
_NOMINATIM_MIN_INTERVAL = 1.0  # seconds — OSM ToS: max 1 req/s


def _cache_key(lat: float, lng: float) -> str:
    """Return a Redis key for a lat/lng pair rounded to 4 decimal places."""
    return f"geocode:{round(lat, 4)}:{round(lng, 4)}"


async def _fetch_from_nominatim(lat: float, lng: float) -> dict:
    """Fetch reverse geocode result from Nominatim, rate-limited to 1 req/s."""
    global _last_nominatim_call

    async with _nominatim_sem:
        # Polite delay: wait until at least 1 s has elapsed since the last call.
        elapsed = time.monotonic() - _last_nominatim_call
        if elapsed < _NOMINATIM_MIN_INTERVAL:
            await asyncio.sleep(_NOMINATIM_MIN_INTERVAL - elapsed)

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
                headers={"User-Agent": "GlobeCRM/0.1 (https://globecrm.app)"},
                timeout=10.0,
            )

        _last_nominatim_call = time.monotonic()

        if response.status_code != 200:
            raise AppException(
                status_code=502,
                code="GEOCODING_ERROR",
                message="Failed to reverse geocode coordinates",
            )

        data = response.json()
        address = data.get("address", {})
        return {
            "country": address.get("country"),
            "city": (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("state")
            ),
            "display_name": data.get("display_name"),
        }


@router.get("/reverse")
async def reverse_geocode(
    lat: float = Query(...),
    lng: float = Query(...),
    _user_id: str = Depends(get_current_user_id),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[dict]:
    """Reverse geocode coordinates to country and city using Nominatim.

    Results are cached in Redis for GEOCODE_CACHE_TTL seconds (default 30 days)
    keyed by lat/lng rounded to 4 decimal places.  Outbound calls to Nominatim
    are rate-limited to 1 request per second to comply with OSM ToS.
    """
    import json

    key = _cache_key(lat, lng)

    # --- Cache hit path ---
    cached = await redis.get(key)
    if cached is not None:
        return ApiResponse(data=json.loads(cached))

    # --- Cache miss: call Nominatim (rate-limited) ---
    result = await _fetch_from_nominatim(lat, lng)

    # Store in cache; ignore Redis errors to preserve graceful-failure behaviour.
    try:
        await redis.set(key, json.dumps(result), ex=GEOCODE_CACHE_TTL)
    except Exception:
        pass

    return ApiResponse(data=result)
