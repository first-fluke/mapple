from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.main import app


async def _override_get_current_user_id() -> int:
    return 1


async def _override_get_session() -> AsyncGenerator[AsyncSession]:
    yield MagicMock(spec=AsyncSession)


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    app.dependency_overrides[get_current_user_id] = _override_get_current_user_id
    app.dependency_overrides[get_session] = _override_get_session

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
