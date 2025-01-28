from contextlib import asynccontextmanager
from fastapi import FastAPI

from source.config import settings
from source.services.database import sessionmanager



@asynccontextmanager
async def lifespan(app: FastAPI, init_db: bool = True):
    if init_db:
        sessionmanager.init(settings.DB_URL)
    print("---> [SERVER STARTED] <---")
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()
    print("---> [SERVER SHUTDOWN] <---")



app = FastAPI(
    title="FastAPI server",
    lifespan=lifespan
)


from source.views.user import router as user_router
app.include_router(user_router, prefix='/user', tags=['user'])




@app.get('')
@app.get('/')
def root():
    return "fastapi + poetry + sqlalchemy + postgresql + alembic + redis + celery + docker"



@app.get('/test')
def test():
    return {"message": "test successful"}




@app.get('/read-env')
def read_env():
    return settings.SECRET_KEY