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





async def test_register_user_request_otp( client: AsyncClient ):
    async with client as ac:
        # register new user
        response = await ac.post( "/user/register", json={
                'username': "test01",
                'email': "test01@email.com",
                'password': "some123",
                'password2': "some123",
                'full_name': "Test User"
            },
        )
        assert response.status_code == 201
        user_data = response.json()
        # login to get access token
        response = await ac.post( url='/auth/login', data={"username": user_data["email"], "password": "some123"} )
        assert response.status_code == 200
        login_data = response.json()

        response = await ac.get( url='/user/request-verification', headers={
                "Authorization" : f"Bearer {login_data['access_token']}"
            }
        )

        verification_data = response.json()
        
        assert type(verification_data['Verification Code']) == str
        assert len(verification_data['Verification Code']) == 7



async def test_register_user_verify_user( client: AsyncClient ):
    async with client as ac:
        # register new user
        response = await ac.post( "/user/register", json={
                'username': "test01",
                'email': "test01@email.com",
                'password': "some123",
                'password2': "some123",
                'full_name': "Test User"
            },
        )
        assert response.status_code == 201
        user_data = response.json()
        assert user_data['is_active'] == False
        # login to get access token
        response = await ac.post( url='/auth/login', data={"username": user_data["email"], "password": "some123"} )
        assert response.status_code == 200
        login_data = response.json()

        response = await ac.get( url='/user/request-verification', headers={
                "Authorization" : f"Bearer {login_data['access_token']}"
            }
        )

        verification_data = response.json()
        
        assert type(verification_data['Verification Code']) == str
        assert len(verification_data['Verification Code']) == 7

        resposne = await ac.post( 
            url='/user/verify-user',
            headers={
                "Authorization": f"Bearer {login_data['access_token']}"
            },
            json={
            "otp": verification_data['Verification Code']
        })

        assert resposne.status_code == 200
        data = resposne.json()
        assert data['result'] == True
        assert data['message'] == "Thank you."