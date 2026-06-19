"""Test configuration and shared fixtures.

JWT tokens produced here include all claims required by src/lib/auth.py:
  sub, exp, iat, jti, iss, aud   (plus kid header = "current")
"""

import datetime
import os
import secrets
import uuid

# Must be set BEFORE any src.* import so auth.py does not raise RuntimeError.
_TEST_SIGNING_KEY = "test-signing-key-for-globe-crm-integration-tests-32b"
os.environ.setdefault("JWT_SIGNING_KEY", _TEST_SIGNING_KEY)
# Legacy alias kept for backward-compat with any remaining JWT_SECRET references.
os.environ.setdefault("JWT_SECRET", _TEST_SIGNING_KEY)

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.auth.models import User
from src.contacts.models import Contact
from src.experiences.models import Experience
from src.lib.auth import (
    JWT_ALGORITHM,
    JWT_AUDIENCE,
    JWT_ISSUER,
    JWT_KID_PRIMARY,
    JWT_SIGNING_KEY,
)
from src.lib.database import Base, get_session
from src.lib.rate_limit import check_data_rate_limit, check_rate_limit
from src.lib.redis import get_redis
from src.main import app
from src.organizations.models import Organization
from src.tags.models import Tag

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://globe:globe@localhost:5432/globe_crm_test",
)

# Exported so security tests can reference the key value directly.
JWT_TEST_SECRET: str = JWT_SIGNING_KEY

test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionFactory = async_sessionmaker(test_engine, expire_on_commit=False)


# ---------------------------------------------------------------------------
# Token helpers (module-level functions, importable from tests)
# ---------------------------------------------------------------------------


def _make_full_token(
    user_id: int | str,
    *,
    secret: str,
    exp_delta: datetime.timedelta = datetime.timedelta(hours=1),
    algorithm: str = JWT_ALGORITHM,
    include_kid: bool = True,
) -> str:
    """Produce a JWT with all claims required by get_current_user_id."""
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + exp_delta).timestamp()),
        "jti": secrets.token_urlsafe(16),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
    }
    headers = {"kid": JWT_KID_PRIMARY} if include_kid else {}
    return jwt.encode(payload, secret, algorithm=algorithm, headers=headers)


def make_auth_headers(user_id: int | str) -> dict[str, str]:
    """Return Authorization headers with a valid Bearer token for the given user_id."""
    token = _make_full_token(user_id, secret=JWT_TEST_SECRET)
    return {"Authorization": f"Bearer {token}"}


def make_expired_token(user_id: int | str = 1) -> str:
    """Return a JWT that is already expired."""
    return _make_full_token(
        user_id,
        secret=JWT_TEST_SECRET,
        exp_delta=datetime.timedelta(seconds=-1),
    )


def make_token_with_secret(user_id: int | str = 1, secret: str = "") -> str:
    """Return a JWT signed with an arbitrary secret (for wrong-secret tests)."""
    return _make_full_token(user_id, secret=secret)


# ---------------------------------------------------------------------------
# DB seeding helpers (module-level async functions, importable from tests)
# ---------------------------------------------------------------------------


async def create_test_user(
    session: AsyncSession,
    *,
    provider_id: str = "google-123",
    email: str = "test@example.com",
    name: str = "Test User",
) -> User:
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        name=name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_test_contact(
    session: AsyncSession,
    *,
    user_id: str,
    name: str = "Contact Name",
    latitude: float | None = None,
    longitude: float | None = None,
) -> Contact:
    contact = Contact(
        user_id=user_id,
        name=name,
        latitude=latitude,
        longitude=longitude,
    )
    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    return contact


async def create_test_organization(
    session: AsyncSession,
    *,
    name: str = "Test Org",
    org_type: str = "company",
) -> Organization:
    org = Organization(name=name, type=org_type)
    session.add(org)
    await session.commit()
    await session.refresh(org)
    return org


async def create_test_tag(
    session: AsyncSession,
    *,
    user_id: str,
    name: str = "test-tag",
    color: str = "#6366f1",
) -> Tag:
    """Create a Tag row owned by the given user."""
    tag = Tag(
        user_id=user_id,
        name=name,
        color=color,
    )
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


async def create_test_experience(
    session: AsyncSession,
    *,
    contact_id: int,
    organization_id: int,
    role: str = "Engineer",
) -> Experience:
    exp = Experience(
        contact_id=contact_id,
        organization_id=organization_id,
        role=role,
    )
    session.add(exp)
    await session.commit()
    await session.refresh(exp)
    return exp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_DB_FIXTURES = {"client", "rate_limit_client", "db_session"}


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Auto-mark any test that requests a DB-backed fixture as ``integration``.

    Runs tryfirst so the marker is in place before pytest evaluates the ``-m``
    deselection expression. Keeps the default run DB-free without per-file edits.
    """
    for item in items:
        if _DB_FIXTURES & set(getattr(item, "fixturenames", ())):
            item.add_marker("integration")


@pytest.fixture(scope="session", autouse=True)
async def setup_database(request):
    """Create all tables before tests, drop after — integration runs only.

    No-op when no integration test is selected, so a DB-free default run never
    opens a connection.
    """
    if not any(item.get_closest_marker("integration") for item in request.session.items):
        yield
        return

    # Import all models so SQLAlchemy metadata is complete.
    import src.auth.models  # noqa: F401
    import src.contact_relationships.models  # noqa: F401
    import src.contacts.models  # noqa: F401
    import src.experiences.models  # noqa: F401
    import src.meetings.models  # noqa: F401
    import src.notifications.models  # noqa: F401
    import src.organizations.models  # noqa: F401
    import src.tags.models  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(autouse=True)
async def cleanup(request):
    """Truncate all tables before each test for isolation — integration only."""
    if request.node.get_closest_marker("integration") is None:
        return
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))


@pytest.fixture
async def db_session():
    """Database session for seeding test data."""
    async with TestSessionFactory() as session:
        yield session


@pytest.fixture
def make_token():
    """Factory to create valid JWT tokens for testing (backward-compat fixture)."""
    def _make(user_id: int = 1, email: str = "test@example.com") -> str:
        return _make_full_token(user_id, secret=JWT_TEST_SECRET)

    return _make


@pytest.fixture
def auth_headers(make_token):
    """Authorization headers with a valid JWT token for user_id=1."""
    return {"Authorization": f"Bearer {make_token()}"}


@pytest.fixture
def fake_redis():
    """Lightweight in-memory Redis substitute for rate-limit and cache tests."""
    store: dict = {}

    class _FakePipeline:
        def __init__(self, redis_obj):
            self._r = redis_obj
            self._queue: list = []

        def set(self, *a, **kw):
            self._queue.append(("set", a, kw))
            return self

        def expire(self, *a, **kw):
            self._queue.append(("expire", a, kw))
            return self

        def sadd(self, *a, **kw):
            self._queue.append(("sadd", a, kw))
            return self

        def delete(self, *a, **kw):
            self._queue.append(("delete", a, kw))
            return self

        async def execute(self):
            results = []
            for cmd, args, kwargs in self._queue:
                results.append(await getattr(self._r, cmd)(*args, **kwargs))
            return results

    class _FakeRedis:
        async def get(self, key: str):
            return store.get(key)

        async def set(self, key: str, value, ex: int | None = None, **_kw):
            store[key] = value

        async def incr(self, key: str) -> int:
            store[key] = store.get(key, 0) + 1
            return store[key]

        async def expire(self, key: str, ttl: int) -> None:
            pass  # TTL not simulated in unit tests

        async def delete(self, *keys: str) -> None:
            for k in keys:
                store.pop(k, None)

        async def sadd(self, key: str, *values) -> int:
            s = store.setdefault(key, set())
            before = len(s)
            s.update(values)
            return len(s) - before

        async def smembers(self, key: str) -> set:
            return set(store.get(key, set()))

        async def ping(self) -> bool:
            return True

        def pipeline(self):
            return _FakePipeline(self)

    return _FakeRedis()


@pytest.fixture
async def client(fake_redis):
    """HTTP client with dependency overrides for testing.

    Rate limiting is bypassed entirely — use `rate_limit_client` for tests
    that need to exercise the actual rate limit logic.
    """

    async def override_get_session():
        async with TestSessionFactory() as session:
            yield session

    async def override_rate_limit():
        pass

    async def override_data_rate_limit():
        pass

    async def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[check_rate_limit] = override_rate_limit
    app.dependency_overrides[check_data_rate_limit] = override_data_rate_limit
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def rate_limit_client(fake_redis):
    """HTTP client with real check_rate_limit and check_data_rate_limit wired to
    fake_redis.

    Use this fixture for tests that need to verify rate limiting behaviour
    (threshold, 429 responses, error shape). The standard `client` fixture
    bypasses rate limits for convenience; this one does not.
    """

    async def override_get_session():
        async with TestSessionFactory() as session:
            yield session

    async def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_redis] = override_get_redis
    # Intentionally NOT overriding check_rate_limit or check_data_rate_limit

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
