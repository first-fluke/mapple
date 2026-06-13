"""Tests for the device token registration endpoints.

Covers:
  - POST /notifications/device-tokens  (register / upsert)
  - GET  /notifications/device-tokens  (list)
  - DELETE /notifications/device-tokens/{token}  (unregister)

Security scenarios tested:
  - Auth is required for every endpoint
  - A user cannot see or delete another user's tokens
  - Invalid platform is rejected with 422
  - Idempotency: re-posting the same token does not duplicate the row
"""

import pytest

from tests.conftest import create_test_user, make_auth_headers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_TOKEN = "fcm-device-token-abc123"
_IOS_PAYLOAD = {"token": _VALID_TOKEN, "platform": "ios"}


# ---------------------------------------------------------------------------
# Auth required
# ---------------------------------------------------------------------------


async def test_register_requires_auth(client):
    resp = await client.post("/notifications/device-tokens", json=_IOS_PAYLOAD)
    assert resp.status_code == 401


async def test_list_requires_auth(client):
    resp = await client.get("/notifications/device-tokens")
    assert resp.status_code == 401


async def test_unregister_requires_auth(client):
    resp = await client.delete(f"/notifications/device-tokens/{_VALID_TOKEN}")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Register (POST)
# ---------------------------------------------------------------------------


async def test_register_creates_row(client, db_session):
    user = await create_test_user(db_session, email="reg@test.com")

    resp = await client.post(
        "/notifications/device-tokens",
        json={"token": "token-xyz", "platform": "android"},
        headers=make_auth_headers(user.id),
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["token"] == "token-xyz"
    assert data["platform"] == "android"
    assert data["user_id"] == user.id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_register_all_platforms(client, db_session):
    user = await create_test_user(db_session, email="platforms@test.com")

    for platform in ("ios", "android", "web"):
        resp = await client.post(
            "/notifications/device-tokens",
            json={"token": f"token-{platform}", "platform": platform},
            headers=make_auth_headers(user.id),
        )
        assert resp.status_code == 201, f"Expected 201 for platform={platform}"
        assert resp.json()["data"]["platform"] == platform


async def test_register_invalid_platform_rejected(client, db_session):
    user = await create_test_user(db_session, email="badplatform@test.com")

    resp = await client.post(
        "/notifications/device-tokens",
        json={"token": "some-token", "platform": "windows"},
        headers=make_auth_headers(user.id),
    )
    assert resp.status_code == 422


async def test_register_missing_token_rejected(client, db_session):
    user = await create_test_user(db_session, email="missing@test.com")

    resp = await client.post(
        "/notifications/device-tokens",
        json={"platform": "ios"},
        headers=make_auth_headers(user.id),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Idempotency: re-register same token does not duplicate
# ---------------------------------------------------------------------------


async def test_register_same_token_is_idempotent(client, db_session):
    user = await create_test_user(db_session, email="idempotent@test.com")
    headers = make_auth_headers(user.id)
    payload = {"token": "stable-token", "platform": "ios"}

    resp1 = await client.post("/notifications/device-tokens", json=payload, headers=headers)
    assert resp1.status_code == 201
    id1 = resp1.json()["data"]["id"]

    resp2 = await client.post("/notifications/device-tokens", json=payload, headers=headers)
    assert resp2.status_code == 201
    id2 = resp2.json()["data"]["id"]

    # Same row — same id, no duplicate
    assert id1 == id2

    # Verify only one row via list endpoint
    list_resp = await client.get("/notifications/device-tokens", headers=headers)
    assert list_resp.status_code == 200
    tokens = list_resp.json()["data"]
    same_token_rows = [t for t in tokens if t["token"] == "stable-token"]
    assert len(same_token_rows) == 1


async def test_register_same_token_updates_platform(client, db_session):
    user = await create_test_user(db_session, email="update_platform@test.com")
    headers = make_auth_headers(user.id)
    token = "cross-platform-token"

    resp1 = await client.post(
        "/notifications/device-tokens",
        json={"token": token, "platform": "ios"},
        headers=headers,
    )
    assert resp1.status_code == 201

    resp2 = await client.post(
        "/notifications/device-tokens",
        json={"token": token, "platform": "web"},
        headers=headers,
    )
    assert resp2.status_code == 201
    # Same id, updated platform
    assert resp1.json()["data"]["id"] == resp2.json()["data"]["id"]
    assert resp2.json()["data"]["platform"] == "web"


# ---------------------------------------------------------------------------
# List (GET)
# ---------------------------------------------------------------------------


async def test_list_returns_only_own_tokens(client, db_session):
    user_a = await create_test_user(db_session, email="list_a@test.com")
    user_b = await create_test_user(db_session, email="list_b@test.com")

    await client.post(
        "/notifications/device-tokens",
        json={"token": "token-a1", "platform": "ios"},
        headers=make_auth_headers(user_a.id),
    )
    await client.post(
        "/notifications/device-tokens",
        json={"token": "token-b1", "platform": "android"},
        headers=make_auth_headers(user_b.id),
    )

    list_resp = await client.get(
        "/notifications/device-tokens",
        headers=make_auth_headers(user_a.id),
    )
    assert list_resp.status_code == 200
    tokens = list_resp.json()["data"]
    assert all(t["user_id"] == user_a.id for t in tokens)
    assert all(t["token"] != "token-b1" for t in tokens)


async def test_list_empty_for_new_user(client, db_session):
    user = await create_test_user(db_session, email="empty@test.com")

    resp = await client.get(
        "/notifications/device-tokens",
        headers=make_auth_headers(user.id),
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []


# ---------------------------------------------------------------------------
# Unregister (DELETE)
# ---------------------------------------------------------------------------


async def test_unregister_removes_token(client, db_session):
    user = await create_test_user(db_session, email="unregister@test.com")
    headers = make_auth_headers(user.id)
    token = "delete-me-token"

    reg = await client.post(
        "/notifications/device-tokens",
        json={"token": token, "platform": "ios"},
        headers=headers,
    )
    assert reg.status_code == 201

    del_resp = await client.delete(
        f"/notifications/device-tokens/{token}",
        headers=headers,
    )
    assert del_resp.status_code == 204

    # Token no longer appears in the list
    list_resp = await client.get("/notifications/device-tokens", headers=headers)
    tokens = list_resp.json()["data"]
    assert all(t["token"] != token for t in tokens)


async def test_unregister_nonexistent_token_returns_404(client, db_session):
    user = await create_test_user(db_session, email="notfound@test.com")

    resp = await client.delete(
        "/notifications/device-tokens/does-not-exist",
        headers=make_auth_headers(user.id),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Cross-user isolation
# ---------------------------------------------------------------------------


async def test_user_cannot_see_other_users_tokens(client, db_session):
    user_a = await create_test_user(db_session, email="iso_a@test.com")
    user_b = await create_test_user(db_session, email="iso_b@test.com")

    await client.post(
        "/notifications/device-tokens",
        json={"token": "secret-a-token", "platform": "ios"},
        headers=make_auth_headers(user_a.id),
    )

    list_resp = await client.get(
        "/notifications/device-tokens",
        headers=make_auth_headers(user_b.id),
    )
    assert list_resp.status_code == 200
    tokens = list_resp.json()["data"]
    assert all(t["token"] != "secret-a-token" for t in tokens)


async def test_user_cannot_delete_other_users_token(client, db_session):
    user_a = await create_test_user(db_session, email="del_a@test.com")
    user_b = await create_test_user(db_session, email="del_b@test.com")

    token = "token-owned-by-a"
    await client.post(
        "/notifications/device-tokens",
        json={"token": token, "platform": "ios"},
        headers=make_auth_headers(user_a.id),
    )

    # User B tries to delete User A's token — should get 404 (not visible)
    resp = await client.delete(
        f"/notifications/device-tokens/{token}",
        headers=make_auth_headers(user_b.id),
    )
    assert resp.status_code == 404

    # User A's token still exists
    list_resp = await client.get(
        "/notifications/device-tokens",
        headers=make_auth_headers(user_a.id),
    )
    tokens = list_resp.json()["data"]
    assert any(t["token"] == token for t in tokens)
