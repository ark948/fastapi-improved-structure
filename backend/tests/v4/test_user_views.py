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




async def test_user_views_test_route(client: AsyncClient):
    async with client as ac:
        response = await ac.get('/user/test')

        assert response.status_code == 200
        assert response.json() == 'ok'




async def test_user_views_get_user_no_data(client: AsyncClient):
    non_existent_user_id = "cace2ccd5cc74bebba7dbef488c7a476f"
    async with client as ac:
        resposne = await ac.get(
            url=f"/user/get-user?id={non_existent_user_id}"
        )

        assert resposne.status_code == 404



        
async def test_user_views_get_user(client: AsyncClient):
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
        assert response.json()["email"] == 'test01@email.com'
        
        user_id = response.json()["id"]

        resposne = await ac.get(
            url=f"/user/get-user?id={user_id}"
        )

        assert resposne.status_code == 200
        assert response.json()["email"] == 'test01@email.com'



async def test_user_views_register(client: AsyncClient):
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
        assert response.json()["email"] == 'test01@email.com'
        
        user_id = response.json()["id"]

        resposne = await ac.get(
            url=f"/user/get-user?id={user_id}"
        )

        assert resposne.status_code == 200
        assert response.json()["email"] == 'test01@email.com'




async def test_user_views_register_missing_email(client: AsyncClient):
    async with client as ac:
        response = await ac.post(
            "/user/register",
            json={
                'username': "test01",
                'password': "some123",
                'password2': "some123",
                'full_name': "Test User"
            },
        )

        # 422 for unprocessable entity (pydantic validation error)
        assert response.status_code == 422

async def test_user_profile(client: AsyncClient):
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
                "username": "test01@email.com",
                "password": "some123"
            }
        )

        assert response.status_code == 200
        login_data = response.json()
        
        response = await ac.get(
            url='/user/profile',
            headers={
                "Authorization": f"Bearer {login_data['access_token']}"
            }
        )

        assert response.status_code == 200


        
async def test_user_profile_invalid_token(client: AsyncClient):
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
                "username": "test01@email.com",
                "password": "some123"
            }
        )

        assert response.status_code == 200
        login_data = response.json()
        
        response = await ac.get(
            url='/user/profile',
            headers={
                "Authorization": f"Bearer lfjldfdjksl{login_data['access_token']}"
            }
        )

        # Unauthorized (invalid authentication credentials)
        assert response.status_code == 401