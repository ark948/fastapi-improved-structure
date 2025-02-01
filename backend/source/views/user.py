from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from source.services.database import get_db
from source.models import User as UserModel
from source.schemas import user as user_schemas
from source.crud import user as user_crud
from source.services.authentication import AuthDep



router = APIRouter()



@router.get("/get-user", response_model=user_schemas.UserBaseModel)
async def get_user(id: str, db: AsyncSession = Depends(get_db)):
    user = await UserModel.get(db, id)
    return user


@router.get("/get-users", response_model=list[user_schemas.UserBaseModel])
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await UserModel.get_all(db)
    return users


@router.post("/create-user", response_model=user_schemas.UserBaseModel, status_code=201)
async def create_user(data: user_schemas.UserCreateModel, db: AsyncSession = Depends(get_db)):
    # user = await UserModel.create(db, **user.dict()) # if not using this, id won't be created
    user = await user_crud.create_user_crud(data, db)
    return user


@router.get('/profile', response_model=user_schemas.UserBaseModel, status_code=status.HTTP_200_OK)
async def profile(user: AuthDep):
    return await user