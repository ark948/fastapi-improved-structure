import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from httpx import AsyncClient


from source.models import User



# pytestmark = pytest.mark.anyio this will freeze the terminal




@pytest.mark.asyncio
async def test_create_user(async_db: AsyncSession):
    existing_users = (await async_db.execute(select(User))).scalars().all()
    assert len(existing_users) == 0

    user = await User.create(
        db=async_db,
        username='test', email='test@test.com', password_hash='somestuff', full_name='Test User'
    )
    await async_db.commit()

    existing_users = (await async_db.execute(select(User))).scalars().all()
    assert len(existing_users) == 1
    assert existing_users[0].email == 'test@test.com'