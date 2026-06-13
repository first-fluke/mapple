"""Regression tests for the contact-scoped avatar flow.

Covers the gap where the web client calls POST /contacts/{id}/avatar/presign
and then PATCH /contacts/{id} with {"avatar_url": ...}, but the API previously
only exposed an unrelated /upload/avatar endpoint and never persisted the URL.

Covers:
- Presign endpoint returns both upload_url and avatar_url for an owned contact.
- Presign on a missing / non-owned contact returns 404.
- PATCH persists avatar_url and it is returned on ContactOut.
- Presign requires authentication.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_test_contact, create_test_user, make_auth_headers


@pytest.fixture
def mock_storage():
    """Mock the MinIO storage client used by the upload service."""
    with patch("src.upload.service.storage") as mock:
        mock.bucket_exists = AsyncMock(return_value=True)
        mock.make_bucket = AsyncMock()
        mock.presigned_put_object = AsyncMock(
            return_value="http://minio:9000/avatars/presigned-put"
        )
        yield mock


@pytest.mark.asyncio
async def test_avatar_presign_returns_upload_and_public_url(
    client: AsyncClient, db_session: AsyncSession, mock_storage
):
    user = await create_test_user(db_session, email="avatar1@test.com")
    contact = await create_test_contact(db_session, user_id=user.id, name="Pic")

    response = await client.post(
        f"/contacts/{contact.id}/avatar/presign",
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["upload_url"] == "http://minio:9000/avatars/presigned-put"
    # Public URL points at the avatars bucket for this user's object.
    assert "/avatars/" in data["avatar_url"]
    assert data["avatar_url"].rstrip("/") != ""


@pytest.mark.asyncio
async def test_avatar_presign_unknown_contact_returns_404(
    client: AsyncClient, db_session: AsyncSession, mock_storage
):
    user = await create_test_user(db_session, email="avatar2@test.com")
    response = await client.post(
        "/contacts/999999/avatar/presign",
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_avatar_presign_other_users_contact_returns_404(
    client: AsyncClient, db_session: AsyncSession, mock_storage
):
    owner = await create_test_user(db_session, email="avatar-owner@test.com")
    other = await create_test_user(db_session, email="avatar-other@test.com")
    contact = await create_test_contact(db_session, user_id=owner.id, name="Owned")

    response = await client.post(
        f"/contacts/{contact.id}/avatar/presign",
        headers=make_auth_headers(other.id),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_persists_avatar_url(
    client: AsyncClient, db_session: AsyncSession
):
    user = await create_test_user(db_session, email="avatar3@test.com")
    contact = await create_test_contact(db_session, user_id=user.id, name="Persist")

    url = "http://cdn.example.com/avatars/abc.jpg"
    response = await client.patch(
        f"/contacts/{contact.id}",
        json={"avatar_url": url},
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 200
    assert response.json()["data"]["avatar_url"] == url

    # And it is reflected on subsequent reads.
    read = await client.get(
        f"/contacts/{contact.id}", headers=make_auth_headers(user.id)
    )
    assert read.status_code == 200
    assert read.json()["data"]["avatar_url"] == url


@pytest.mark.asyncio
async def test_avatar_presign_requires_auth(client: AsyncClient):
    response = await client.post("/contacts/1/avatar/presign")
    assert response.status_code in (401, 403)
