import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://globe:globe@localhost:5432/globe_crm",
)

# Supabase Supavisor (transaction mode, port 6543) reuses prepared statement
# cache slots across clients, which conflicts with asyncpg's default per-conn
# prepared statement caching. Disable both caches when running through the
# pooler. Direct (5432) connections work fine with these set to 0 too.
engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
