"""Security tests for file upload and presigned URL handling.

Covers:
- Content-type validation (only image/* allowed)
- Path traversal prevention in content-type
- Presigned URL scoping and isolation
- Upload authentication requirements
"""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import make_auth_headers


@pytest.fixture
def mock_storage():
    """Mock the MinIO storage client."""
    with patch("src.upload.service.storage") as mock:
        mock.bucket_exists = AsyncMock(return_value=True)
        mock.presigned_put_object = AsyncMock(
            return_value="http://minio:9000/avatars/test-presigned-url"
        )
        yield mock


# --- Content-type validation ---


VALID_IMAGE_TYPES = [
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "image/svg+xml",
]

INVALID_CONTENT_TYPES = [
    "application/pdf",
    "application/javascript",
    "text/html",
    "text/plain",
    "application/x-executable",
    "application/octet-stream",
    "video/mp4",
    "audio/mp3",
    "multipart/form-data",
]


@pytest.mark.parametrize("content_type", VALID_IMAGE_TYPES)
async def test_valid_image_content_types_accepted(
    client, content_type, mock_storage
):
    """Valid image content types must be accepted."""
    response = await client.post(
        "/upload/avatar",
        json={"content_type": content_type},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 201


@pytest.mark.parametrize("content_type", INVALID_CONTENT_TYPES)
async def test_non_image_content_types_rejected(
    client, content_type, mock_storage
):
    """Non-image content types must be rejected (422 validation error)."""
    response = await client.post(
        "/upload/avatar",
        json={"content_type": content_type},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 422


# --- Path traversal in content-type ---


PATH_TRAVERSAL_PAYLOADS = [
    "image/../../etc/passwd",
    "image/../../../.env",
    "image/png; charset=utf-8\nX-Injected: header",
]


@pytest.mark.parametrize("payload", PATH_TRAVERSAL_PAYLOADS)
async def test_path_traversal_in_content_type(client, payload, mock_storage):
    """Path traversal attempts in content_type must not affect object path."""
    response = await client.post(
        "/upload/avatar",
        json={"content_type": payload},
        headers=make_auth_headers(1),
    )
    if response.status_code == 201:
        data = response.json()["data"]
        object_name = data["object_name"]
        # Object name must not contain directory traversal sequences
        assert "../" not in object_name
        # Object name must start with user_id/
        assert object_name.startswith("1/")


@pytest.mark.xfail(
    strict=True,
    reason="Null bytes in content_type pass Pydantic regex validation and reach the object name",
)
async def test_null_byte_in_content_type_rejected(client, mock_storage):
    """Null bytes in content_type must be rejected to prevent truncation attacks."""
    response = await client.post(
        "/upload/avatar",
        json={"content_type": "image/png\x00.html"},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 422


# --- Presigned URL isolation ---


async def test_presigned_url_scoped_to_user_id(client, mock_storage):
    """Presigned URL object path must be prefixed with the authenticated user's ID."""
    user_id = 42
    response = await client.post(
        "/upload/avatar",
        json={"content_type": "image/png"},
        headers=make_auth_headers(user_id),
    )
    assert response.status_code == 201

    # Verify the storage was called with user_id prefix
    call_args = mock_storage.presigned_put_object.call_args
    object_name = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("object_name")
    assert object_name.startswith(f"{user_id}/")


async def test_presigned_url_uses_uuid_filename(client, mock_storage):
    """Presigned URL must use UUID-based filenames to prevent guessing."""
    import re

    response = await client.post(
        "/upload/avatar",
        json={"content_type": "image/png"},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 201
    data = response.json()["data"]

    # Object name should be {user_id}/{uuid}.{ext}
    uuid_pattern = r"^\d+/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.png$"
    assert re.match(uuid_pattern, data["object_name"]), (
        f"Object name '{data['object_name']}' does not use UUID format"
    )


async def test_presigned_url_has_expiry(client, mock_storage):
    """Presigned URL response must include expiry information."""
    response = await client.post(
        "/upload/avatar",
        json={"content_type": "image/png"},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 201
    data = response.json()["data"]

    assert "expires_in" in data
    assert isinstance(data["expires_in"], int)
    assert data["expires_in"] > 0
    # Expiry should be reasonable (not more than 1 hour)
    assert data["expires_in"] <= 3600


# --- Authentication requirements ---


async def test_upload_requires_authentication(client, mock_storage):
    """Upload endpoint must reject unauthenticated requests."""
    response = await client.post(
        "/upload/avatar",
        json={"content_type": "image/png"},
    )
    assert response.status_code in (401, 403)


# --- Content-type edge cases ---


async def test_empty_content_type_rejected(client, mock_storage):
    """Empty content_type must be rejected."""
    response = await client.post(
        "/upload/avatar",
        json={"content_type": ""},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 422


async def test_missing_content_type_rejected(client, mock_storage):
    """Missing content_type field must be rejected."""
    response = await client.post(
        "/upload/avatar",
        json={},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 422


async def test_content_type_case_sensitivity(client, mock_storage):
    """Content-type validation should handle case variations."""
    response = await client.post(
        "/upload/avatar",
        json={"content_type": "IMAGE/PNG"},
        headers=make_auth_headers(1),
    )
    # The regex pattern ^image/ is case-sensitive, so IMAGE/ should be rejected
    assert response.status_code == 422
