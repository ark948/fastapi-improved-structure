from sqlalchemy_utils import database_exists
from sqlalchemy.util import greenlet_spawn
import asyncio

url = "postgresql+asyncpg://arman:123@localhost:5434/test02"
async def check(url):
    url = "postgresql+asyncpg://arman:123@localhost:5434/test02"
    result = await greenlet_spawn(database_exists(url))
    return result



if __name__ == "__main__":
    asyncio.run(check("postgresql+asyncpg://arman:123@localhost:5434/test02"))