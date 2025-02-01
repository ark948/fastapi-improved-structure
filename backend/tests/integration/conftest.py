from typing import AsyncGenerator
from uuid import UUID, uuid4
import pytest
from httpx import AsyncClient, ASGITransport
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



# database 'test02' must exist in postgresql server
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




@pytest.fixture()
async def client( connection: AsyncConnection, transaction: AsyncTransaction ) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        async_session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )
        async with async_session:
            yield async_session
    
    app.dependency_overrides[get_db] = override_get_async_session
    yield AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        )
    del app.dependency_overrides[get_db]
    await transaction.rollback()