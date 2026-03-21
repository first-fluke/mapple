import time
from unittest.mock import AsyncMock, patch

import httpx
import pytest

ITERATIONS = 100
WARMUP = 10
P95_THRESHOLD_MS = 200


def _p95(latencies: list[float]) -> float:
    """Return the 95th-percentile value from a list of latencies in ms."""
    ordered = sorted(latencies)
    idx = int(len(ordered) * 0.95)
    return ordered[idx]


@pytest.mark.asyncio
async def test_health_p95(client: httpx.AsyncClient) -> None:
    # Warmup phase
    for _ in range(WARMUP):
        await client.get("/health")

    # Measurement phase
    latencies: list[float] = []
    for _ in range(ITERATIONS):
        start = time.perf_counter()
        resp = await client.get("/health")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        latencies.append(elapsed_ms)

    p95 = _p95(latencies)
    assert p95 < P95_THRESHOLD_MS, f"p95 latency {p95:.2f}ms exceeds {P95_THRESHOLD_MS}ms threshold"


@pytest.mark.asyncio
async def test_organizations_search_p95(client: httpx.AsyncClient) -> None:
    with patch(
        "src.organizations.service.OrganizationService.search",
        new_callable=AsyncMock,
        return_value=[],
    ):
        # Warmup phase
        for _ in range(WARMUP):
            await client.get("/organizations")

        # Measurement phase
        latencies: list[float] = []
        for _ in range(ITERATIONS):
            start = time.perf_counter()
            resp = await client.get("/organizations")
            elapsed_ms = (time.perf_counter() - start) * 1000
            assert resp.status_code == 200
            latencies.append(elapsed_ms)

    p95 = _p95(latencies)
    assert p95 < P95_THRESHOLD_MS, f"p95 latency {p95:.2f}ms exceeds {P95_THRESHOLD_MS}ms threshold"
