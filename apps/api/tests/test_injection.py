"""Security tests for injection attacks (SQLi, XSS, SSTI).

Covers OWASP A03 (Injection) with focus on:
- SQL injection via organization search (ILIKE parameter)
- SQL injection via path parameters
- Stored XSS via organization/experience fields
- Error message information leakage
"""

import pytest

from tests.conftest import (
    create_test_contact,
    create_test_organization,
    create_test_user,
    make_auth_headers,
)

# --- SQL Injection payloads for organization search ---

SQL_INJECTION_PAYLOADS = [
    # Classic SQL injection
    "'; DROP TABLE organization; --",
    "' OR '1'='1",
    "' OR 1=1 --",
    "' UNION SELECT 1,2,3,4,5 --",
    # Boolean-based blind SQLi
    "' AND 1=1 --",
    "' AND 1=2 --",
    # Time-based blind SQLi
    "'; SELECT pg_sleep(5) --",
    "' OR pg_sleep(5) --",
    # Stacked queries
    "'; INSERT INTO user_auth (provider,provider_id,email) VALUES ('evil','x','evil@test.com'); --",
    # UNION-based extraction
    "' UNION SELECT id,email,name,provider,provider_id FROM user_auth --",
    # Comment-based
    "admin'/*",
    "*/OR 1=1/*",
    # Encoded payloads
    "%27%20OR%201%3D1%20--",
]


@pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
async def test_sql_injection_via_org_search(client, db_session, payload):
    """Organization search must be safe from SQL injection.

    The ILIKE query uses SQLAlchemy ORM which parameterizes queries,
    preventing SQL injection. This test verifies that invariant.
    """
    user = await create_test_user(db_session)
    await create_test_organization(db_session, name="Safe Org")

    response = await client.get(
        "/organizations",
        params={"q": payload},
        headers=make_auth_headers(user.id),
    )
    # Must not cause a 500 error (would indicate SQL parsing issue)
    assert response.status_code == 200

    # Must not return data from other tables (UNION injection)
    data = response.json()["data"]
    for item in data:
        assert "email" not in item or item.get("type") is not None
        assert set(item.keys()) == {"id", "name", "type"}


async def test_sql_injection_org_search_returns_no_extra_data(client, db_session):
    """SQL injection in search must not leak data from other tables."""
    user = await create_test_user(db_session, email="secret@company.com")
    await create_test_organization(db_session, name="Visible Org")

    # Attempt UNION injection to extract user emails
    response = await client.get(
        "/organizations",
        params={"q": "' UNION SELECT 1, email, provider FROM user_auth --"},
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 200
    data = response.json()["data"]

    # Verify no user data leaked
    for item in data:
        assert "secret@company.com" not in str(item)


# --- SQL Injection via path parameters ---


async def test_sql_injection_via_contact_id_path_param(client, db_session):
    """Path parameter contact_id must be validated as integer."""
    user = await create_test_user(db_session)

    # FastAPI auto-validates path params as int, should return 422
    response = await client.get(
        "/contacts/1 OR 1=1/experiences",
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 422


async def test_sql_injection_via_experience_id_path_param(client, db_session):
    """Path parameter experience_id must be validated as integer."""
    user = await create_test_user(db_session)

    response = await client.delete(
        "/contacts/1/experiences/1; DROP TABLE experience",
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 422


# --- Stored XSS prevention ---

XSS_PAYLOADS = [
    '<script>alert("xss")</script>',
    '<img src=x onerror=alert("xss")>',
    '<svg onload=alert("xss")>',
    "javascript:alert('xss')",
    '<a href="javascript:alert(1)">click</a>',
    '"><script>alert(document.cookie)</script>',
    "' onfocus=alert(1) autofocus='",
    '<iframe src="javascript:alert(1)">',
    "${alert(1)}",
    "{{7*7}}",  # SSTI payload
]


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
async def test_xss_stored_via_org_name(client, db_session, payload):
    """XSS payloads stored in organization names must be returned as-is (escaped by frontend).

    The API stores data as-is and relies on frontend frameworks (React)
    to escape output. This test verifies the API doesn't crash on XSS payloads
    and returns them as plain text (not interpreted as HTML).
    """
    user = await create_test_user(db_session)

    response = await client.post(
        "/organizations",
        json={"name": payload, "type": "test"},
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 201
    data = response.json()["data"]

    # The payload must be stored and returned as a plain string
    assert data["name"] == payload

    # Verify Content-Type is application/json (not text/html)
    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
async def test_xss_stored_via_experience_role(client, db_session, payload):
    """XSS payloads in experience role field must be handled safely."""
    user = await create_test_user(db_session)
    org = await create_test_organization(db_session)
    contact = await create_test_contact(db_session, user_id=user.id)

    response = await client.post(
        f"/contacts/{contact.id}/experiences",
        json={"organization_id": org.id, "role": payload},
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["role"] == payload
    assert "application/json" in response.headers.get("content-type", "")


async def test_xss_reflected_via_org_search(client, db_session):
    """XSS payloads in search queries must not be reflected unsafely."""
    user = await create_test_user(db_session)

    xss = '<script>alert("reflected")</script>'
    response = await client.get(
        "/organizations",
        params={"q": xss},
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")

    # The XSS payload must not appear in a text/html response
    raw = response.text
    if xss in raw:
        # It's in JSON, which is safe as long as Content-Type is application/json
        assert "text/html" not in response.headers.get("content-type", "")


# --- Error message information leakage ---


async def test_invalid_provider_does_not_leak_internals(client):
    """Invalid OAuth provider must not leak stack traces or internal details."""
    response = await client.post(
        "/auth/token",
        json={
            "provider": "evil_provider",
            "code": "fake-code",
            "redirect_uri": "http://evil.com",
        },
    )
    body = response.json()
    body_str = str(body)

    # Must not contain stack traces or internal paths
    assert "Traceback" not in body_str
    assert "/src/" not in body_str
    assert "sqlalchemy" not in body_str.lower()
    assert "postgresql" not in body_str.lower()


async def test_validation_error_does_not_leak_schema(client):
    """Validation errors must not expose internal schema details excessively."""
    response = await client.post(
        "/organizations",
        json={},
        headers=make_auth_headers(1),
    )
    # Pydantic validation error - should return 422 but not internal model names
    assert response.status_code == 422
    body_str = str(response.json())
    assert "OrganizationCreate" not in body_str or "field required" in body_str.lower()


# --- Input length/boundary tests ---


async def test_org_name_max_length_enforced(client, db_session):
    """Organization name exceeding max_length must be rejected."""
    await create_test_user(db_session)
    response = await client.post(
        "/organizations",
        json={"name": "A" * 256, "type": "company"},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 422


async def test_org_type_max_length_enforced(client, db_session):
    """Organization type exceeding max_length must be rejected."""
    await create_test_user(db_session)
    response = await client.post(
        "/organizations",
        json={"name": "Test", "type": "X" * 51},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 422


async def test_experience_role_max_length_enforced(client, db_session):
    """Experience role exceeding max_length must be rejected."""
    user = await create_test_user(db_session)
    org = await create_test_organization(db_session)
    contact = await create_test_contact(db_session, user_id=user.id)

    response = await client.post(
        f"/contacts/{contact.id}/experiences",
        json={"organization_id": org.id, "role": "R" * 256},
        headers=make_auth_headers(user.id),
    )
    assert response.status_code == 422


async def test_search_query_max_length_enforced(client, db_session):
    """Search query exceeding max_length must be rejected."""
    await create_test_user(db_session)
    response = await client.get(
        "/organizations",
        params={"q": "A" * 256},
        headers=make_auth_headers(1),
    )
    assert response.status_code == 422
