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





async def test_auth_views_successful_login( client: AsyncClient ):
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

        assert response.status_code == 201

        response = await ac.post(
            url='/auth/login',
            data={
                "username": "test01@email.com",
                "password": "some123"
            }
        )

        assert response.status_code == 200




async def test_auth_views_unsuccessful_login( client: AsyncClient ):
    async with client as ac:
        response = await ac.post(
            "/user/register",
            json={'username': "test01",
                'email': "test01@email.com",
                'password': "some123",
                'password2': "some123",
                'full_name': "Test User"})

        assert response.status_code == 201

        response = await ac.post(
            url='/auth/login',
            data={
                "username": "test02@email.com",
                "password": "some444"
            }
        )

        assert response.status_code == 401
        data = response.json()
        
        assert data["detail"] == "Incorrect username or password"