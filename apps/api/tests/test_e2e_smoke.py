"""
E2E Smoke Tests for Globe CRM API (Hybrid Stack)

These tests verify the deployed API endpoints work correctly against
a real running instance (Fly.io, local, or any target).

Usage:
  # Against local dev
  uv run pytest tests/test_e2e_smoke.py -v

  # Against deployed Fly.io instance
  E2E_API_URL=https://globe-crm-api.fly.dev uv run pytest tests/test_e2e_smoke.py -v

  # With auth (session token from better-auth)
  E2E_API_URL=https://globe-crm-api.fly.dev E2E_SESSION_TOKEN=<token> uv run pytest tests/test_e2e_smoke.py -v
"""

import os

import httpx
import pytest

API_URL = os.environ.get("E2E_API_URL", "http://localhost:8000")
SESSION_TOKEN = os.environ.get("E2E_SESSION_TOKEN", "")

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def api():
    """HTTP client for E2E API calls."""
    headers = {}
    if SESSION_TOKEN:
        headers["Authorization"] = f"Bearer {SESSION_TOKEN}"
    with httpx.Client(base_url=API_URL, headers=headers, timeout=30) as client:
        yield client


# ---------------------------------------------------------------------------
# 1. Health Check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    def test_api_health(self, api: httpx.Client):
        """Verify API is reachable and healthy."""
        resp = api.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"


# ---------------------------------------------------------------------------
# 2. Auth Endpoints
# ---------------------------------------------------------------------------


class TestAuth:
    def test_unauthenticated_request_returns_401(self):
        """Verify protected endpoints reject unauthenticated requests."""
        with httpx.Client(base_url=API_URL, timeout=30) as client:
            resp = client.get("/auth/me")
            assert resp.status_code == 401

    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_get_current_user(self, api: httpx.Client):
        """Verify /auth/me returns current user profile."""
        resp = api.get("/auth/me")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "id" in data
        assert "email" in data
        assert "name" in data


# ---------------------------------------------------------------------------
# 3. Contact CRUD
# ---------------------------------------------------------------------------


class TestContactCRUD:
    """Full CRUD lifecycle for contacts. Requires auth."""

    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_contact_lifecycle(self, api: httpx.Client):
        """Create → Read → Update → Delete a contact."""
        # Create
        create_resp = api.post(
            "/contacts",
            json={
                "name": "E2E Smoke Test Contact",
                "email": "e2e-smoke@test.example",
                "phone": "+1-555-0199",
                "latitude": 37.5665,
                "longitude": 126.978,
                "country": "South Korea",
                "city": "Seoul",
            },
        )
        assert create_resp.status_code == 201
        contact = create_resp.json()["data"]
        contact_id = contact["id"]
        assert contact["name"] == "E2E Smoke Test Contact"
        assert contact["latitude"] == pytest.approx(37.5665, abs=0.001)
        assert contact["longitude"] == pytest.approx(126.978, abs=0.001)

        try:
            # Read
            get_resp = api.get(f"/contacts/{contact_id}")
            assert get_resp.status_code == 200
            assert get_resp.json()["data"]["id"] == contact_id

            # Update
            update_resp = api.patch(
                f"/contacts/{contact_id}",
                json={"name": "E2E Updated Contact", "city": "Busan"},
            )
            assert update_resp.status_code == 200
            assert update_resp.json()["data"]["name"] == "E2E Updated Contact"
            assert update_resp.json()["data"]["city"] == "Busan"

            # List with search
            list_resp = api.get("/contacts", params={"q": "E2E Updated"})
            assert list_resp.status_code == 200
            contacts = list_resp.json()["data"]
            assert any(c["id"] == contact_id for c in contacts)
        finally:
            # Delete (cleanup)
            del_resp = api.delete(f"/contacts/{contact_id}")
            assert del_resp.status_code == 204


# ---------------------------------------------------------------------------
# 4. PostGIS Bounding Box Query (Globe)
# ---------------------------------------------------------------------------


class TestGlobeBbox:
    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_globe_data_with_bbox(self, api: httpx.Client):
        """Verify /globe/data returns contacts within bounding box."""
        # Seoul area bounding box
        resp = api.get(
            "/globe/data",
            params={"bbox": "126.0,37.0,128.0,38.0"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "contacts" in data
        assert "relationships" in data
        assert "clusters" in data
        assert isinstance(data["contacts"], list)

    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_globe_data_etag_caching(self, api: httpx.Client):
        """Verify ETag caching returns 304 on second request."""
        bbox = "126.0,37.0,128.0,38.0"
        resp1 = api.get("/globe/data", params={"bbox": bbox})
        assert resp1.status_code == 200

        etag = resp1.headers.get("etag")
        if etag:
            resp2 = api.get(
                "/globe/data",
                params={"bbox": bbox},
                headers={"If-None-Match": etag},
            )
            assert resp2.status_code == 304

    def test_globe_data_invalid_bbox(self, api: httpx.Client):
        """Verify invalid bbox returns 400."""
        resp = api.get("/globe/data", params={"bbox": "invalid"})
        # Returns 401 without auth or 400 with auth for invalid bbox
        assert resp.status_code in (400, 401, 422)


# ---------------------------------------------------------------------------
# 5. Avatar Upload (Presigned URL)
# ---------------------------------------------------------------------------


class TestAvatarUpload:
    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_avatar_presigned_url(self, api: httpx.Client):
        """Verify avatar upload returns a presigned URL."""
        resp = api.post(
            "/upload/avatar",
            json={"content_type": "image/png"},
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert "url" in data
        assert "object_name" in data
        assert "expires_in" in data
        assert data["expires_in"] > 0
        assert data["url"].startswith("http")

    def test_avatar_upload_requires_auth(self):
        """Verify avatar upload requires authentication."""
        with httpx.Client(base_url=API_URL, timeout=30) as client:
            resp = client.post(
                "/upload/avatar",
                json={"content_type": "image/png"},
            )
            assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 6. Redis Cache (Graph Endpoints)
# ---------------------------------------------------------------------------


class TestGraphCache:
    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_graph_edges(self, api: httpx.Client):
        """Verify graph edges endpoint responds (uses Redis cache)."""
        resp = api.get("/graph/edges", params={"type": "COMPANY"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_graph_clusters(self, api: httpx.Client):
        """Verify graph clusters endpoint responds (uses Redis cache)."""
        resp = api.get("/graph/clusters", params={"type": "SCHOOL"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_graph_cache_consistency(self, api: httpx.Client):
        """Verify repeated requests return consistent results (cache hit)."""
        resp1 = api.get("/graph/edges", params={"type": "COMPANY"})
        resp2 = api.get("/graph/edges", params={"type": "COMPANY"})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json() == resp2.json()


# ---------------------------------------------------------------------------
# 7. Tags CRUD
# ---------------------------------------------------------------------------


class TestTags:
    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_tag_lifecycle(self, api: httpx.Client):
        """Create → List → Update → Delete a tag."""
        # Create
        create_resp = api.post(
            "/tags",
            json={"name": "e2e-smoke-tag", "color": "#ff5733"},
        )
        assert create_resp.status_code == 201
        tag = create_resp.json()["data"]
        tag_id = tag["id"]

        try:
            # List
            list_resp = api.get("/tags")
            assert list_resp.status_code == 200
            tags = list_resp.json()["data"]
            assert any(t["id"] == tag_id for t in tags)

            # Update
            update_resp = api.patch(
                f"/tags/{tag_id}",
                json={"name": "e2e-updated-tag", "color": "#33ff57"},
            )
            assert update_resp.status_code == 200
            assert update_resp.json()["data"]["name"] == "e2e-updated-tag"
        finally:
            # Delete (cleanup)
            del_resp = api.delete(f"/tags/{tag_id}")
            assert del_resp.status_code == 204


# ---------------------------------------------------------------------------
# 8. Organizations
# ---------------------------------------------------------------------------


class TestOrganizations:
    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_organization_create_and_search(self, api: httpx.Client):
        """Create an organization and search for it."""
        resp = api.post(
            "/organizations",
            json={"name": "E2E Smoke Corp", "type": "company"},
        )
        assert resp.status_code == 201
        org = resp.json()["data"]
        assert org["name"] == "E2E Smoke Corp"

        # Search
        search_resp = api.get("/organizations", params={"q": "E2E Smoke"})
        assert search_resp.status_code == 200
        orgs = search_resp.json()["data"]
        assert any(o["id"] == org["id"] for o in orgs)


# ---------------------------------------------------------------------------
# 9. Export
# ---------------------------------------------------------------------------


class TestExport:
    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_export_contacts_csv(self, api: httpx.Client):
        """Verify CSV export endpoint returns valid response."""
        resp = api.get("/export/contacts")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
        assert "attachment" in resp.headers.get("content-disposition", "")


# ---------------------------------------------------------------------------
# 10. Meetings
# ---------------------------------------------------------------------------


class TestMeetings:
    @pytest.mark.skipif(not SESSION_TOKEN, reason="E2E_SESSION_TOKEN not set")
    def test_meetings_list(self, api: httpx.Client):
        """Verify meetings list endpoint responds."""
        resp = api.get("/meetings")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
