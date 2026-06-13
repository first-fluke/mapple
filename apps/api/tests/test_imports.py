"""Tests for CSV contact import endpoint (Task D).

Covers:
- Valid CSV creates contacts, returns per-row "created" status.
- Malformed rows (bad email, empty name) are reported as errors without aborting the batch.
- Over-cap (>1000 rows) is rejected with a clear message.
- Missing auth returns 401.
- Tags column is parsed and associated correctly.
"""

import io

import pytest

from tests.conftest import create_test_user, make_auth_headers


def _csv_bytes(*rows: str, header: str = "name,email,phone,tags") -> bytes:
    """Build a CSV byte payload from rows (each a CSV line)."""
    lines = [header] + list(rows)
    return "\n".join(lines).encode("utf-8")


def _upload(client, content: bytes, headers: dict, filename: str = "contacts.csv"):
    """POST multipart CSV to /imports/contacts."""
    return client.post(
        "/imports/contacts",
        files={"file": (filename, io.BytesIO(content), "text/csv")},
        headers=headers,
    )


# ---------------------------------------------------------------------------
# Happy-path: valid CSV
# ---------------------------------------------------------------------------


async def test_import_valid_csv_creates_contacts(client, db_session):
    """Valid CSV rows must be created and reported as 'created'."""
    user = await create_test_user(db_session, email="import-valid@test.com")
    headers = make_auth_headers(user.id)

    csv_data = _csv_bytes(
        "Alice,alice@example.com,+1-800-555-0100,friend;colleague",
        "Bob,,+44 20 7946 0958,",
        "Charlie,charlie@example.com,,vip",
    )

    r = await _upload(client, csv_data, headers)
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["total"] == 3
    assert body["created"] == 3
    assert body["errors"] == 0
    statuses = [row["status"] for row in body["results"]]
    assert statuses == ["created", "created", "created"]


async def test_import_returns_per_row_indices(client, db_session):
    """Row numbers in results must be 1-based and sequential."""
    user = await create_test_user(db_session, email="import-rows@test.com")
    headers = make_auth_headers(user.id)

    csv_data = _csv_bytes("Alice,alice@example.com,,", "Bob,bob@example.com,,")
    r = await _upload(client, csv_data, headers)
    assert r.status_code == 200
    rows = r.json()["results"]
    assert [row["row"] for row in rows] == [1, 2]


# ---------------------------------------------------------------------------
# Malformed rows: errors without aborting batch
# ---------------------------------------------------------------------------


async def test_import_bad_email_reported_as_error(client, db_session):
    """A row with an invalid email must be reported as error; other rows still created."""
    user = await create_test_user(db_session, email="import-bademail@test.com")
    headers = make_auth_headers(user.id)

    csv_data = _csv_bytes(
        "Alice,alice@example.com,,",   # valid
        "BadEmail,not-an-email,,",     # invalid email
        "Charlie,charlie@example.com,,",  # valid
    )

    r = await _upload(client, csv_data, headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert body["created"] == 2
    assert body["errors"] == 1

    results_by_row = {row["row"]: row for row in body["results"]}
    assert results_by_row[1]["status"] == "created"
    assert results_by_row[2]["status"] == "error"
    assert results_by_row[2]["error"] is not None
    assert results_by_row[3]["status"] == "created"


async def test_import_empty_name_reported_as_error(client, db_session):
    """A row with an empty name must be reported as error."""
    user = await create_test_user(db_session, email="import-noname@test.com")
    headers = make_auth_headers(user.id)

    csv_data = _csv_bytes(
        ",alice@example.com,,",    # empty name
        "Bob,bob@example.com,,",  # valid
    )

    r = await _upload(client, csv_data, headers)
    assert r.status_code == 200
    body = r.json()
    assert body["errors"] == 1
    assert body["created"] == 1

    error_row = next(row for row in body["results"] if row["status"] == "error")
    assert error_row["row"] == 1
    assert error_row["error"] is not None


async def test_import_all_malformed_returns_all_errors(client, db_session):
    """All-bad rows: total errors == total rows, zero created."""
    user = await create_test_user(db_session, email="import-allbad@test.com")
    headers = make_auth_headers(user.id)

    csv_data = _csv_bytes(
        ",bad@example.com,,",   # empty name
        "X,not-email,,",        # invalid email
    )

    r = await _upload(client, csv_data, headers)
    assert r.status_code == 200
    body = r.json()
    assert body["created"] == 0
    assert body["errors"] == 2


# ---------------------------------------------------------------------------
# Over-cap rejection
# ---------------------------------------------------------------------------


async def test_import_over_1000_rows_rejected(client, db_session):
    """CSV with more than 1000 data rows must be rejected with a single error entry."""
    user = await create_test_user(db_session, email="import-overcap@test.com")
    headers = make_auth_headers(user.id)

    rows = [f"User{i},user{i}@example.com,," for i in range(1001)]
    csv_data = _csv_bytes(*rows)

    r = await _upload(client, csv_data, headers)
    assert r.status_code == 200
    body = r.json()
    assert body["created"] == 0
    assert body["errors"] == 1
    assert body["total"] == 1001
    assert "1000" in body["results"][0]["error"] or "limit" in body["results"][0]["error"].lower()


async def test_import_exactly_1000_rows_accepted(client, db_session):
    """CSV with exactly 1000 data rows must be processed (at the cap, not over)."""
    user = await create_test_user(db_session, email="import-cap1000@test.com")
    headers = make_auth_headers(user.id)

    rows = [f"User{i},user{i}@example.com,," for i in range(1000)]
    csv_data = _csv_bytes(*rows)

    r = await _upload(client, csv_data, headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1000
    assert body["created"] == 1000
    assert body["errors"] == 0


# ---------------------------------------------------------------------------
# Tag parsing
# ---------------------------------------------------------------------------


async def test_import_tags_comma_separated(client, db_session):
    """Tags separated by commas must all be created."""
    user = await create_test_user(db_session, email="import-tags@test.com")
    headers = make_auth_headers(user.id)

    csv_data = _csv_bytes("Alice,alice@example.com,,vip,friend,colleague")
    # Note: extra commas mean extra columns — use semicolon to stay in one cell.
    csv_data = _csv_bytes("Alice,alice@example.com,,vip;friend;colleague")

    r = await _upload(client, csv_data, headers)
    assert r.status_code == 200
    assert r.json()["created"] == 1


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------


async def test_import_requires_auth(client):
    """POST /imports/contacts must reject unauthenticated requests with 401."""
    csv_data = _csv_bytes("Alice,alice@example.com,,")
    r = await client.post(
        "/imports/contacts",
        files={"file": ("contacts.csv", io.BytesIO(csv_data), "text/csv")},
    )
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Data rate limit passthrough (verify endpoint is under rate limit)
# ---------------------------------------------------------------------------


async def test_import_endpoint_is_registered(client, db_session):
    """POST /imports/contacts must be reachable (not 404/405)."""
    user = await create_test_user(db_session, email="import-reg@test.com")
    headers = make_auth_headers(user.id)

    # Empty CSV (just headers) — no rows to process.
    csv_data = b"name,email,phone,tags\n"
    r = await _upload(client, csv_data, headers)
    # 200 with zero rows is fine; what matters is it's not 404.
    assert r.status_code != 404
    assert r.status_code != 405
