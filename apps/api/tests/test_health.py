"""Tests for the health endpoint.

Decision: FIXED TEST — endpoint returns {"status": "ok"|"degraded", "checks": {"db": bool, "redis": bool}}.
The old test expected {"status": "ok"} with no checks key. The richer shape is
the correct current behaviour — updated to assert real shape.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "checks" in body
    assert "db" in body["checks"]
    assert "redis" in body["checks"]
