from typing import Annotated, Dict
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
from source.dependencies import SessionDep



router = APIRouter()



@router.get('/test', response_model=str, status_code=200)
async def test():
    return 'ok'



@router.get("/get-user", response_model=user_schemas.UserBaseModel | None)
async def get_user(id: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await User.get(db, id)
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"There was a problem. {str(error)}"
        )
    if user:
        return user
    raise HTTPException(
        status_code=404, detail="User not found."
    )

@router.get("/get-users", response_model=list[user_schemas.UserBaseModel])
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await User.get_all(db)
    return users


@router.post("/register", response_model=user_schemas.UserBaseModel, status_code=201)
async def create_user(data: user_schemas.UserCreateModel, db: AsyncSession = Depends(get_db)):
    # user = await UserModel.create(db, **user.dict()) # if not using this, id won't be created
    user = await user_crud.create_user_crud(data, db)
    return user


@router.get('/profile', response_model=user_schemas.UserBaseModel, status_code=status.HTTP_200_OK)
async def profile(current_user: AuthDep):
    return current_user


@router.get('/request-verification', response_model=dict, status_code=status.HTTP_200_OK)
async def request_verification(current_user: AuthDep, r: RedisDep):
    otp = utils.generate_otp()
    result = await submit_otp_for_user(otp=otp, user_id=current_user.id, redis_client=r)
    return {
        "Verification Code": otp,
        "message": "Please use this code to verify your account, it will be valid for 10 minutes.",
        "link": "http://127.0.0.1:8000/auth/verify-user"
    }



@router.post('/verify-user', response_model=dict, status_code=200)
async def verify_user(otp: Annotated[str, Body(embed=True)], current_user: AuthDep, r: RedisDep, db: SessionDep):
    status = await verify_otp_for_user( otp_input=otp, user_id_input=current_user.id, redis_client=r)
    if status:
        result = await user_crud.activate_user_crud(current_user, db)
        if result:
            return {
                "result": "True",
                "message": "Thank you."
            }