from typing import AsyncGenerator
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Importing fastapi.Depends that is used to retrieve SQLAlchemy's session
from source.services.database import get_db
# Importing main FastAPI instance
from source.main import app
from source.models import User

# To run async tests
pytestmark = pytest.mark.anyio



async def test_create_user(session: AsyncSession):
    existing_users = (await session.execute(select(User))).scalars().all()
    assert len(existing_users) == 0

    user = await User.create(
        db=session,
        username='test', email='test@test.com', password_hash='somestuff', full_name='Test User'
    )
    await session.commit()

    existing_users = (await session.execute(select(User))).scalars().all()
    assert len(existing_users) == 1
    assert existing_users[0].email == 'test@test.com'


async def test_rollbacks_between_functions(session: AsyncSession):
    current_users = (await session.execute(select(User))).scalars().all()
    assert len(current_users) == 0


# Tests showing rollbacks between functions when using API client
async def test_api_create_user(client: AsyncClient):
    async with client as ac:
        response = await ac.post(
            "/user/register",
            json={
                'username': "test01",
                'email': "test01@email.com",
                'password': "some123",
                'password2': "some123",
                'full_name': "Test User"
            },
        )
        created_user_id = response.json()["id"]

        response = await ac.get(
            "/user/get-users",
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        response = await ac.get(
            f"/user/get-user?id={created_user_id}",
        )
        assert response.status_code == 200
        assert response.json()["id"] == created_user_id
        assert response.json()["username"] == 'test01'


async def test_client_rollbacks( client: AsyncClient ):
    async with client as ac:
        resposne = await ac.get("/user/get-users")
        assert resposne.status_code == 200
        assert len(resposne.json()) == 0