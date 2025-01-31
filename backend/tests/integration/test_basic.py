import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from source.models import User



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