from source.api.routers import users, user_roles, roles, auth
from fastapi import APIRouter



api_router = APIRouter()




api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(user_roles.router, prefix='/users-roles', tags=['user-roles'])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
