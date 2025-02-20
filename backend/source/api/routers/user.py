from typing import Any, List

from source.schemas.user import UserCreate, User as SchemaUser, UserBaseModel
# from source import crud, models, schemas
from source.api import deps
from source.constants.role import Role
from source.config import settings
from fastapi import APIRouter, Body, Depends, HTTPException, Security
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from pydantic.types import UUID4
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession


from source.services.database import get_db
from source.services.authentication import get_user_from_email
from source.crud.user import create_user_with_role
from source.dependencies import SessionDep
from source.models import User
from source.crud.user import crud_user_get_by_email
from source.utils import myprint




router = APIRouter()



# bare asterisk means the all parameters after asterisk must be keyword params

@router.post("/create", response_model=SchemaUser)
async def create_user(
    *,
    db: SessionDep,
    user_in: UserCreate,
    current_user: User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
        )
) -> Any:
    """
    Create new user.
    """
    user = await get_user_from_email(user_in.email, db)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this username already exists in the system.",
        )
    user = await create_user_with_role(user_in, db)
    return user



@router.post("/open", response_model=UserBaseModel)
async def create_user_open(
    *,
    db: AsyncSession = Depends(get_db),
    email: EmailStr = Body(...),
    username: str = Body(...),
    full_name: str = Body(...),
    password: str = Body(...),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException( status_code=403, detail="Open user registration is forbidden on this server" )
    user = await crud_user_get_by_email(email, db)
    if user:
        raise HTTPException( status_code=409, detail="The user with this username already exists in the system", )       
    user_in = UserCreate( password=password, email=email, full_name=full_name, username=username )
    user = await create_user_with_role(obj_in=user_in, db=db)
    return user
