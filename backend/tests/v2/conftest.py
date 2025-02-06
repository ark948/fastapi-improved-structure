from typing import AsyncGenerator
from uuid import UUID, uuid4
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine, AsyncTransaction, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlalchemy.util import greenlet_spawn
import pytest_asyncio
from alembic import command
from alembic.config import Config



from source.services.database import get_db, Base
from source.main import app
from source.models import User


db_url = "postgresql+asyncpg://arman:123@localhost:5434/test02"



@pytest.fixture(scope="session")
def anyio_backend():
    print("\nFixture 1\n")
    return "asyncio"



import os
from sqlalchemy.pool import NullPool


async_engine = create_async_engine(
    url=db_url,
    echo=False,
    poolclass=NullPool,
)


# Drop all tables after each test
@pytest_asyncio.fixture(scope="function")
async def async_db_engine():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_db(async_db_engine):
    async_session = async_sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def async_client(async_db):
    def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")



