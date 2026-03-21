import datetime
import os

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-globe-crm-integration-tests")

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.lib.auth import JWT_ALGORITHM, JWT_SECRET
from src.lib.database import Base, get_session
from src.lib.rate_limit import check_rate_limit
from src.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://globe:globe@localhost:5432/globe_crm_test",
)

test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionFactory = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables before tests, drop after."""
    import src.auth.models  # noqa: F401
    import src.contacts.models  # noqa: F401
    import src.experiences.models  # noqa: F401
    import src.organizations.models  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(autouse=True)
async def cleanup():
    """Truncate all tables before each test for isolation."""
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))


@pytest.fixture
async def db_session():
    """Database session for seeding test data. Remember to commit()."""
    async with TestSessionFactory() as session:
        yield session


@pytest.fixture
def make_token():
    """Factory to create JWT tokens for testing."""
    secret = JWT_SECRET or "test-secret-key-for-globe-crm-integration-tests"

    def _make(user_id: int = 1, email: str = "test@example.com") -> str:
        now = datetime.datetime.now(datetime.UTC)
        payload = {
            "sub": str(user_id),
            "email": email,
            "iat": now,
            "exp": now + datetime.timedelta(hours=1),
        }
        return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)

    return _make


@pytest.fixture
def auth_headers(make_token):
    """Authorization headers with a valid JWT token for user_id=1."""
    return {"Authorization": f"Bearer {make_token()}"}


@pytest.fixture
async def client():
    """HTTP client with dependency overrides for testing."""

    async def override_get_session():
        async with TestSessionFactory() as session:
            yield session

    async def override_rate_limit():
        pass

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[check_rate_limit] = override_rate_limit

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
