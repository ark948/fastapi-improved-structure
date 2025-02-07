from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from source.config import settings
from source.services.database import sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI, init_db: bool = True):
    if init_db:
        sessionmanager.init(settings.DB_URL)
    print("\t---> [SERVER STARTED] <---")
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()
    print("\t---> [SERVER SHUTDOWN] <---")


app = FastAPI(
    title="FastAPI server",
    lifespan=lifespan
)


from source.views.user import router as user_router
app.include_router(user_router, prefix='/user', tags=['user'])

from source.services.authentication import router as auth_router
app.include_router(auth_router, prefix='/auth', tags=['auth'])


app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('')
@app.get('/')
def root():
    return "fastapi + poetry + sqlalchemy + postgresql + alembic + redis + celery + docker"


@app.get('/test')
def test():
    return {"message": "test successful"}


# This is just to test if env file was properly loaded.
# DELETE THIS IN PRODUCTION
@app.get('/read-env')
def read_env():
    return settings.SECRET_KEY


@app.get('/health')
def health_check():
    return {'message': "سلام"}