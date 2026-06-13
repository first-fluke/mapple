"""Security tests for rate limiting.

Covers:
- Auth endpoint rate limiting (IP-based)
- Upload endpoint rate limiting (user-based)
- Rate limit response codes and headers

Decision (cluster 4): FIXED TEST
  - All /auth/refresh bodies changed from {"refresh_token": ...} to {"refresh": ...}
    to match the current RefreshRequest Pydantic schema.
  - All /auth/logout bodies changed from {"refresh_token": ...} to {"refresh": ...}
    to match the current LogoutRequest Pydantic schema.
  - Logout is POST /auth/logout (not DELETE /auth/logout).
  - Tests that verify 429 responses now use the `rate_limit_client` fixture
    (which has real rate limiting wired to fake_redis) instead of `client`
    (which bypasses rate limiting entirely for convenience).
"""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import make_auth_headers


# --- Auth endpoint rate limiting ---


async def test_auth_rate_limit_allows_under_threshold(rate_limit_client, fake_redis):
    """Auth endpoints must allow requests under the rate limit threshold."""
    # Default rate limit is 10 requests per 60 seconds
    for i in range(10):
        response = await rate_limit_client.post(
            "/auth/refresh",
            json={"refresh": f"token-{i}"},
        )
        # Should get 401 (invalid token) but NOT 429
        assert response.status_code != 429, f"Rate limited on request {i + 1}"


async def test_auth_rate_limit_blocks_over_threshold(rate_limit_client, fake_redis):
    """Auth endpoints must return 429 when rate limit is exceeded."""
    # Exceed the rate limit (default: 10 requests per 60 seconds)
    for i in range(11):
        response = await rate_limit_client.post(
            "/auth/refresh",
            json={"refresh": f"token-{i}"},
        )

    # The 11th request should be rate limited
    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "RATE_LIMITED"


async def test_auth_rate_limit_applies_to_all_auth_endpoints(rate_limit_client, fake_redis):
    """Rate limit counter must be shared across all /auth/* endpoints."""
    # Mix different auth endpoints to fill the rate limit
    for i in range(5):
        await rate_limit_client.post(
            "/auth/refresh",
            json={"refresh": f"token-{i}"},
        )
    for i in range(5):
        await rate_limit_client.post(
            "/auth/logout",
            json={"refresh": f"token-{i}"},
        )

    # 11th request (any auth endpoint) should be rate limited
    response = await rate_limit_client.post(
        "/auth/refresh",
        json={"refresh": "final-token"},
    )
    assert response.status_code == 429


# --- Upload rate limiting ---


@pytest.fixture
def mock_storage():
    with patch("src.upload.service.storage") as mock:
        mock.bucket_exists = AsyncMock(return_value=True)
        mock.presigned_put_object = AsyncMock(
            return_value="http://minio:9000/avatars/test-url"
        )
        yield mock


async def test_upload_rate_limit_allows_under_threshold(
    client, fake_redis, mock_storage
):
    """Upload endpoint must allow requests under the rate limit (5/60s)."""
    headers = make_auth_headers(1)
    for i in range(5):
        response = await client.post(
            "/upload/avatar",
            json={"content_type": "image/png"},
            headers=headers,
        )
        assert response.status_code != 429, f"Rate limited on request {i + 1}"


async def test_upload_rate_limit_blocks_over_threshold(
    rate_limit_client, fake_redis, mock_storage
):
    """Upload endpoint must return 429 when rate limit is exceeded (>5/60s)."""
    headers = make_auth_headers(1)
    for i in range(6):
        response = await rate_limit_client.post(
            "/upload/avatar",
            json={"content_type": "image/png"},
            headers=headers,
        )

    # The 6th request should be rate limited
    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "RATE_LIMITED"


async def test_upload_rate_limit_is_per_user(rate_limit_client, fake_redis, mock_storage):
    """Upload rate limit must be per-user, not global."""
    # User 1 exhausts their rate limit
    headers_1 = make_auth_headers(1)
    for i in range(6):
        await rate_limit_client.post(
            "/upload/avatar",
            json={"content_type": "image/png"},
            headers=headers_1,
        )

    # User 2 should still be able to upload
    headers_2 = make_auth_headers(2)
    response = await rate_limit_client.post(
        "/upload/avatar",
        json={"content_type": "image/png"},
        headers=headers_2,
    )
    assert response.status_code == 201


async def test_rate_limit_error_response_format(rate_limit_client, fake_redis):
    """Rate limit responses must have consistent error format."""
    for i in range(11):
        response = await rate_limit_client.post(
            "/auth/refresh",
            json={"refresh": f"token-{i}"},
        )

    assert response.status_code == 429
    body = response.json()

    # Must follow standard error response format
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]
    assert body["error"]["code"] == "RATE_LIMITED"

    # Must not leak rate limit implementation details
    assert "redis" not in body["error"]["message"].lower()
    assert "rate:auth" not in body["error"]["message"]


# --- Data endpoint rate limiting (Task B) ---


async def test_data_rate_limit_applied_to_contacts(client, db_session):
    """Data routers (contacts) must be registered under check_data_rate_limit.

    The client fixture bypasses both rate limiters, so we verify the dependency
    is wired by inspecting the router's dependency list directly — not by
    hitting the limit (which would require 120+ requests).
    """
    from fastapi import Depends

    from src.contacts.router import router as contacts_router
    from src.lib.rate_limit import check_data_rate_limit

    # Check that check_data_rate_limit appears in the router's dependencies.
    dep_calls = [str(dep.dependency) for dep in contacts_router.dependencies]
    assert any("check_data_rate_limit" in d for d in dep_calls), (
        "check_data_rate_limit not found in contacts router dependencies. "
        f"Found: {dep_calls}"
    )


async def test_data_rate_limit_applied_to_all_data_routers():
    """All data routers must have check_data_rate_limit in their router-level dependencies."""
    from src.contacts.router import router as contacts_router
    from src.experiences.router import router as experiences_router
    from src.geocoding.router import router as geocoding_router
    from src.globe.router import router as globe_router
    from src.graph.router import router as graph_router
    from src.imports.router import router as imports_router
    from src.lib.rate_limit import check_data_rate_limit
    from src.meetings.router import router as meetings_router
    from src.organizations.router import router as organizations_router
    from src.tags.router import router as tags_router

    routers = {
        "contacts": contacts_router,
        "experiences": experiences_router,
        "geocoding": geocoding_router,
        "globe": globe_router,
        "graph": graph_router,
        "imports": imports_router,
        "meetings": meetings_router,
        "organizations": organizations_router,
        "tags": tags_router,
    }

    for name, router in routers.items():
        dep_fns = [dep.dependency for dep in router.dependencies]
        assert check_data_rate_limit in dep_fns, (
            f"Router '{name}' is missing check_data_rate_limit in its router-level dependencies."
        )
