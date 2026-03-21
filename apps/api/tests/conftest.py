import datetime
import os

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-globe-crm-integration-tests")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-security-tests")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

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
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from src.auth.models import UserAuth
from src.contacts.models import Contact
from src.experiences.models import Experience
from src.lib.redis import get_redis
from src.organizations.models import Organization
JWT_TEST_SECRET = os.environ["JWT_SECRET"]
class FakeRedis:
    """Minimal async Redis mock for testing."""
    def __init__(self) -> None:
        self._store: dict[str, str] = {}
    async def get(self, key: str) -> str | None:
        return self._store.get(key)
    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self._store[key] = str(value)
        return True
    async def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._store:
                del self._store[key]
                count += 1
        return count
    async def incr(self, key: str) -> int:
        val = int(self._store.get(key, "0")) + 1
        self._store[key] = str(val)
        return val
    async def expire(self, key: str, seconds: int) -> bool:
    async def aclose(self) -> None:
        pass
def make_auth_headers(user_id: int, **extra_claims: object) -> dict[str, str]:
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": str(user_id),
        "email": f"user{user_id}@test.com",
        "iat": now,
        "exp": now + datetime.timedelta(minutes=15),
        **extra_claims,
    }
    token = jwt.encode(payload, JWT_TEST_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}
def make_expired_token(user_id: int = 1) -> str:
        "iat": now - datetime.timedelta(hours=1),
        "exp": now - datetime.timedelta(minutes=1),
    return jwt.encode(payload, JWT_TEST_SECRET, algorithm="HS256")
def make_token_with_secret(user_id: int, secret: str) -> str:
    return jwt.encode(payload, secret, algorithm="HS256")


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
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    @event.listens_for(engine.sync_engine, "connect")
    def enable_foreign_keys(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
    await engine.dispose()
def fake_redis():
    return FakeRedis()
async def client(db_session, fake_redis):
        yield db_session
    async def override_get_redis():
        return fake_redis
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

# --- Data factories ---
async def create_test_user(
    session: AsyncSession,
    *,
    provider: str = "google",
    provider_id: str = "provider-123",
    email: str = "test@example.com",
    name: str | None = "Test User",
) -> UserAuth:
    user = UserAuth(
        provider=provider,
        provider_id=provider_id,
        email=email,
        name=name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
async def create_test_contact(
    user_id: int,
    name: str = "Test Contact",
    email: str | None = "contact@example.com",
    phone: str | None = None,
) -> Contact:
    contact = Contact(
        user_id=user_id,
        phone=phone,
    session.add(contact)
    await session.refresh(contact)
    return contact
async def create_test_organization(
    name: str = "Test Org",
    org_type: str = "company",
) -> Organization:
    org = Organization(name=name, type=org_type)
    session.add(org)
    await session.refresh(org)
    return org
async def create_test_experience(
    contact_id: int,
    organization_id: int,
    role: str | None = "Engineer",
    major: str | None = None,
) -> Experience:
    exp = Experience(
        contact_id=contact_id,
        organization_id=organization_id,
        role=role,
        major=major,
    session.add(exp)
    await session.refresh(exp)
    return exp
from collections.abc import AsyncGenerator
from unittest.mock import MagicMock
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
async def _override_get_current_user_id() -> int:
    return 1
async def _override_get_session() -> AsyncGenerator[AsyncSession]:
    yield MagicMock(spec=AsyncSession)
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    app.dependency_overrides[get_current_user_id] = _override_get_current_user_id
    app.dependency_overrides[get_session] = _override_get_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
