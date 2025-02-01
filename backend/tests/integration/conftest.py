from typing import AsyncGenerator
from uuid import UUID, uuid4
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine, AsyncTransaction, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlalchemy.util import greenlet_spawn
import pytest_asyncio



from source.services.database import get_db, Base
from source.main import app
from source.models import User


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"




@pytest.fixture(scope="session")
async def connection( anyio_backend ) -> AsyncGenerator[AsyncConnection, None]:
    engine = create_async_engine("postgresql+asyncpg://arman:123@localhost:5434/test02")
    async with engine.connect() as connection:
        yield connection



@pytest.fixture()
async def transaction( connection: AsyncConnection ) -> AsyncGenerator[AsyncTransaction, None]:
    async with connection.begin() as transaction:
        yield transaction


@pytest.fixture()
async def session( connection: AsyncConnection, transaction: AsyncTransaction ) -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )
    yield async_session
    await transaction.rollback()