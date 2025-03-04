from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from source.config import settings
from source.services.database import sessionmanager
from source.services.rate import limiter, _rate_limit_exceeded_handler


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

app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)



@app.get('/test-rate-limit')
@limiter.limit("5/minute")
async def test_rate_limit(request: Request):
    return PlainTextResponse("This route is rate limited.")



@app.get('/test-rate-limit02')
@limiter.limit('10/minute', key_func=lambda request: request.state.user_role)
async def test_rate_limit02(request: Request):
    return Response({"message": f"This endpoint is rate limited to 10 requests per minute based on user roles"})



from source.views.user import router as user_router
app.include_router(user_router, prefix='/user', tags=['user'])

# from source.services.authentication import router as auth_router
# app.include_router(auth_router, prefix='/auth', tags=['auth'])

from source.apps.accounts.views import acc_router
from source.apps.accounts.views import pages_router
app.include_router(acc_router, prefix='/accounts')
app.include_router(pages_router, prefix='/pages')


from source.api.endpoints import api_router
app.include_router(api_router, prefix='/api')


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