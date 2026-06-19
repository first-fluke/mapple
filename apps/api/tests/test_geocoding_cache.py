"""Tests for geocoding Redis cache + Nominatim politeness (Task C).

Strategy:
- Mock httpx.AsyncClient.get so no real network calls are made.
- Assert the mock is called exactly once for two identical requests (cache hit on second).
- Assert the cached result is returned correctly.
- Assert graceful failure when Nominatim returns non-200.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from tests.conftest import create_test_user, make_auth_headers


def _make_nominatim_response(country: str = "South Korea", city: str = "Seoul") -> MagicMock:
    """Build a mock httpx.Response that looks like a successful Nominatim reply."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "display_name": f"{city}, {country}",
        "address": {
            "country": country,
            "city": city,
        },
    }
    return mock_resp


async def test_geocode_cache_hit_skips_nominatim(client, db_session, fake_redis):
    """Second identical geocode request must be served from Redis (Nominatim called once)."""
    user = await create_test_user(db_session, email="geocache@test.com")
    headers = make_auth_headers(user.id)

    # We need the router to use our fake_redis. The `client` fixture already overrides
    # get_redis to return fake_redis, so the geocoding endpoint will use it.
    mock_resp = _make_nominatim_response()

    # Patch the httpx.AsyncClient used inside _fetch_from_nominatim.
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_ctx.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_ctx

        # First request — cache miss, Nominatim is called.
        r1 = await client.get(
            "/geocoding/reverse",
            params={"lat": 37.5665, "lng": 126.9780},
            headers=headers,
        )
        assert r1.status_code == 200
        data1 = r1.json()["data"]
        assert data1["country"] == "South Korea"
        assert data1["city"] == "Seoul"

        # Second request — same coords, should hit cache (Nominatim NOT called again).
        r2 = await client.get(
            "/geocoding/reverse",
            params={"lat": 37.5665, "lng": 126.9780},
            headers=headers,
        )
        assert r2.status_code == 200
        data2 = r2.json()["data"]
        assert data2["country"] == "South Korea"

        # Nominatim HTTP client was called exactly once across both requests.
        assert mock_ctx.get.call_count == 1, (
            f"Expected Nominatim to be called once, but it was called "
            f"{mock_ctx.get.call_count} times — cache is not working."
        )


async def test_geocode_different_coords_both_call_nominatim(client, db_session, fake_redis):
    """Different lat/lng pairs must each trigger a separate Nominatim call."""
    user = await create_test_user(db_session, email="geodiff@test.com")
    headers = make_auth_headers(user.id)

    mock_resp = _make_nominatim_response()
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_ctx.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_ctx

        await client.get(
            "/geocoding/reverse",
            params={"lat": 37.5665, "lng": 126.9780},
            headers=headers,
        )
        await client.get(
            "/geocoding/reverse",
            params={"lat": 48.8566, "lng": 2.3522},  # Paris
            headers=headers,
        )

        assert mock_ctx.get.call_count == 2


async def test_geocode_rounded_coords_share_cache(client, db_session, fake_redis):
    """Coordinates that round to the same 4-decimal value must share a cache entry."""
    user = await create_test_user(db_session, email="georound@test.com")
    headers = make_auth_headers(user.id)

    mock_resp = _make_nominatim_response()
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_ctx.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_ctx

        # 37.56650 and 37.56651 both round to 37.5665 at 4 decimal places.
        await client.get(
            "/geocoding/reverse",
            params={"lat": 37.56650, "lng": 126.97800},
            headers=headers,
        )
        await client.get(
            "/geocoding/reverse",
            params={"lat": 37.56651, "lng": 126.97801},
            headers=headers,
        )

        # Both share the same cache key — Nominatim called only once.
        assert mock_ctx.get.call_count == 1


async def test_geocode_nominatim_error_returns_502(client, db_session, fake_redis):
    """When Nominatim returns non-200, the endpoint must return 502 gracefully."""
    user = await create_test_user(db_session, email="geoerr@test.com")
    headers = make_auth_headers(user.id)

    mock_resp = MagicMock()
    mock_resp.status_code = 503

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_ctx.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_ctx

        r = await client.get(
            "/geocoding/reverse",
            params={"lat": 0.0, "lng": 0.0},
            headers=headers,
        )

    assert r.status_code == 502
    body = r.json()
    assert body["error"]["code"] == "GEOCODING_ERROR"


async def test_geocode_requires_auth(client):
    """GET /geocoding/reverse must reject unauthenticated requests with 401."""
    r = await client.get("/geocoding/reverse", params={"lat": 37.5, "lng": 127.0})
    assert r.status_code == 401
