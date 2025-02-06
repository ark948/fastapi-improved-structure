import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from httpx import AsyncClient


from source.models import User



pytestmark = pytest.mark.anyio




async def test_main_test_route( client: AsyncClient ):
    async with client as ac:
        response = await ac.get(f'/user/get-user?id={1}')
        assert response.status_code == 404