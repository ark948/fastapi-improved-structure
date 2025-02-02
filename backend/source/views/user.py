from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from source.services.database import get_db
from source.models import User
from source.schemas import user as user_schemas
from source.crud import user as user_crud
from source.services.authentication import AuthDep, get_current_user
from source import utils
from source.services.redis import submit_otp_for_user, verify_otp_for_user, RedisDep



router = APIRouter()



@router.get("/get-user", response_model=user_schemas.UserBaseModel)
async def get_user(id: str, db: AsyncSession = Depends(get_db)):
    user = await User.get(db, id)
    return user


@router.get("/get-users", response_model=list[user_schemas.UserBaseModel])
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await User.get_all(db)
    return users


@router.post("/create-user", response_model=user_schemas.UserBaseModel, status_code=201)
async def create_user(data: user_schemas.UserCreateModel, db: AsyncSession = Depends(get_db)):
    # user = await UserModel.create(db, **user.dict()) # if not using this, id won't be created
    user = await user_crud.create_user_crud(data, db)
    return user


@router.get('/profile', response_model=user_schemas.UserBaseModel, status_code=status.HTTP_200_OK)
async def profile(current_user: AuthDep):
    return current_user


@router.get('/request-verification', response_model=dict, status_code=status.HTTP_200_OK)
async def request_verification(r: RedisDep, user: AuthDep):
    otp = utils.generate_otp()
    result = await submit_otp_for_user(user.id, otp=int(otp), redis_client=r)
    return {
        "Verification Code": int(otp),
        "message": "Please use this code to verify your account, it will be valid for 10 minutes.",
        "link": "http://127.0.0.1:8000/auth/verify-user"
    }



@router.post('/verify-user', response_model=str, status_code=200)
async def verify_user(r: RedisDep, user: AuthDep, otp: Annotated[int, Body(embed=True)]):
    result = await verify_otp_for_user(user.id, otp_input=int(otp), redis_client=r)
    if result:
        return "OK"