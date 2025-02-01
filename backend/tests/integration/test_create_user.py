import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from httpx import AsyncClient


from source.models import User



pytestmark = pytest.mark.anyio




async def test_user_views_create_user_valid( client: AsyncClient ):
    async with client as ac:
        response = await ac.post(
            "/user/create-user",
            json={
                'username': "test01",
                'email': "test01@email.com",
                'password': "some123",
                'password2': "some123",
                'full_name': "Test User"
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == 'test01'
        assert data["email"] == 'test01@email.com'
        assert data["full_name"] == 'Test User'
        with pytest.raises(KeyError):
            assert data["password"] == None
        with pytest.raises(KeyError):
            assert data["password2"] == None
        with pytest.raises(KeyError):
            assert data["password_hash"] == None



async def test_user_views_get_all_users( client: AsyncClient ):
    async with client as ac:
        response = await ac.get('/user/get-users')
        data = response.json()
        assert len(data) == 0

        response = await ac.post(
            "/user/create-user",
            json={
                'username': "test01",
                'email': "test01@email.com",
                'password': "some123",
                'password2': "some123",
                'full_name': "Test User"
            },
        )

        response = await ac.get('/user/get-users')
        data = response.json()
        assert len(data) == 1