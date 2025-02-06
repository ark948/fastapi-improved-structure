from typing import AsyncGenerator
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine, AsyncTransaction
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlalchemy.util import greenlet_spawn


# Importing fastapi.Depends that is used to retrieve SQLAlchemy's session
from source.services.database import Base
from source.services.database import get_db
from source.models import User
# Importing main FastAPI instance
from source.main import app


db_url = "postgresql+asyncpg://arman:123@localhost:5434/test02"

# Supply connection string
engine = create_async_engine("postgresql+asyncpg://arman:123@localhost:5434/test02")



# Required per https://anyio.readthedocs.io/en/stable/testing.html#using-async-fixtures-with-higher-scopes
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# database existed
# table got created

# attempting to remvoe both, see what happens,
# starting with table... result: table users gets created.

# now attempting to remove database:
# result: database 'test02' does not exist
# attempting to create databse and try again...
# result: OK, tests pass

# Now in v4, i will try to see if i can automate the creation of database

# Update: got database_exists to return True, and tests pass


@pytest.fixture(scope="session")
async def connection(anyio_backend) -> AsyncGenerator[AsyncConnection, None]:
    def check_db_exists():
        result = database_exists("postgresql+asyncpg://arman:123@localhost:5434/test02")
        return result
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    await init_models()
    result = await greenlet_spawn(check_db_exists)
    print("\n\n", result, "\n\n")
    async with engine.connect() as connection:
        yield connection

        
@pytest.fixture()
async def transaction(
    connection: AsyncConnection,
) -> AsyncGenerator[AsyncTransaction, None]:
    async with connection.begin() as transaction:
        yield transaction


# Use this fixture to get SQLAlchemy's AsyncSession.
# All changes that occur in a test function are rolled back
# after function exits, even if session.commit() is called
# in inner functions
@pytest.fixture()
async def session(
    connection: AsyncConnection, transaction: AsyncTransaction
) -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )
    yield async_session
    await transaction.rollback()



# Use this fixture to get HTTPX's client to test API.
# All changes that occur in a test function are rolled back
# after function exits, even if session.commit() is called
# in FastAPI's application endpoints
@pytest.fixture()
async def client(
    connection: AsyncConnection, transaction: AsyncTransaction
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        async_session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )
        async with async_session:
            yield async_session
    
    # Here you have to override the dependency that is used in FastAPI's
    # endpoints to get SQLAlchemy's AsyncSession. In my case, it is
    # get_async_session
    app.dependency_overrides[get_db] = override_get_async_session
    yield AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    )
    del app.dependency_overrides[get_db]

    await transaction.rollback()


