"""Security tests for rate limiting.

Covers:
- Auth endpoint rate limiting (IP-based)
- Upload endpoint rate limiting (user-based)
- Rate limit response codes and headers
"""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import make_auth_headers


# --- Auth endpoint rate limiting ---


async def test_auth_rate_limit_allows_under_threshold(client, fake_redis):
    """Auth endpoints must allow requests under the rate limit threshold."""
    # Default rate limit is 10 requests per 60 seconds
    for i in range(10):
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": f"token-{i}"},
        )
        # Should get 401 (invalid token) but NOT 429
        assert response.status_code != 429, f"Rate limited on request {i + 1}"


async def test_auth_rate_limit_blocks_over_threshold(client, fake_redis):
    """Auth endpoints must return 429 when rate limit is exceeded."""
    # Exceed the rate limit (default: 10 requests per 60 seconds)
    for i in range(11):
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": f"token-{i}"},
        )

    # The 11th request should be rate limited
    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "RATE_LIMITED"


async def test_auth_rate_limit_applies_to_all_auth_endpoints(client, fake_redis):
    """Rate limit counter must be shared across all /auth/* endpoints."""
    # Mix different auth endpoints to fill the rate limit
    for i in range(5):
        await client.post(
            "/auth/refresh",
            json={"refresh_token": f"token-{i}"},
        )
    for i in range(5):
        await client.request(
            "DELETE",
            "/auth/logout",
            json={"refresh_token": f"token-{i}"},
        )

    # 11th request (any auth endpoint) should be rate limited
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": "final-token"},
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
    client, fake_redis, mock_storage
):
    """Upload endpoint must return 429 when rate limit is exceeded (>5/60s)."""
    headers = make_auth_headers(1)
    for i in range(6):
        response = await client.post(
            "/upload/avatar",
            json={"content_type": "image/png"},
            headers=headers,
        )

    # The 6th request should be rate limited
    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "RATE_LIMITED"


async def test_upload_rate_limit_is_per_user(client, fake_redis, mock_storage):
    """Upload rate limit must be per-user, not global."""
    # User 1 exhausts their rate limit
    headers_1 = make_auth_headers(1)
    for i in range(6):
        await client.post(
            "/upload/avatar",
            json={"content_type": "image/png"},
            headers=headers_1,
        )

    # User 2 should still be able to upload
    headers_2 = make_auth_headers(2)
    response = await client.post(
        "/upload/avatar",
        json={"content_type": "image/png"},
        headers=headers_2,
    )
    assert response.status_code == 201


async def test_rate_limit_error_response_format(client, fake_redis):
    """Rate limit responses must have consistent error format."""
    for i in range(11):
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": f"token-{i}"},
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
