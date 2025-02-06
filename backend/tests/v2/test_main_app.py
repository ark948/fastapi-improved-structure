import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from httpx import AsyncClient


from source.models import User



# pytestmark = pytest.mark.anyio this will freeze the terminal
# use @pytest.mark.asyncio


@pytest.mark.asyncio
async def test_main_app_test_route( async_client: AsyncClient ):
    async with async_client as ac:
        response = await ac.get('/test')

        assert response.status_code == 200
        assert response.json()['message'] == 'test successful'



@pytest.mark.asyncio
async def test_main_app_root( async_client: AsyncClient ):
    async with async_client as ac:
        response = await ac.get('/')

        assert response.status_code == 200
        assert response.json() == "fastapi + poetry + sqlalchemy + postgresql + alembic + redis + celery + docker"