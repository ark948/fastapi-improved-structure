from contextlib import asynccontextmanager
from fastapi import FastAPI

from source.config import settings
from source.services.database import sessionmanager


def init_app(init_db=True):
    lifespan = None

    if init_db:
        sessionmanager.init(settings.DB_URL)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    server = FastAPI(title="FastAPI server", lifespan=lifespan)

    from source.views.user import router as user_router
    server.include_router(user_router, prefix="/api", tags=["user"])

    return server