from datetime import timedelta
from typing import Any

from sqlalchemy import select
from source.crud import user as crud
from source.models import User, Role
from source.schemas import user as user_schemas
from source.schemas.user import User as SchemaUser
from source.schemas.token import Token, TokenPayload
from source.constants.role import Role as ConstantRole
from source.api import deps
from source.services import security
from source.config import settings
from fastapi import APIRouter, Body, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession
from source.dependencies import SessionDep
from source.api.deps import CurrentUserDep
from source.services import authentication
from source.utils import myprint



router = APIRouter()



@router.post("/access-token", response_model=Token | None)
async def login_access_token(
    db: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user_crud.authenticate( db, email=form_data.username, password=form_data.password )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    if not await crud.is_user_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token_payload = {
        "id": user.id,
    }
    if not user.user_role:
        token_payload["role"] = "GUEST"
    else:
        role = await db.get(Role, user.user_role.role_id)
        token_payload["role"] = role.name
    return {
        "access_token": security.create_access_token(
            token_payload, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }



@router.post("/test-token", response_model=SchemaUser)
async def test_token(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/hash-password", response_model=str)
async def hash_password(password: str = Body(..., embed=True),) -> Any:
    """
    Hash a password
    """
    return security.get_password_hash(password)


@router.get("/test-token")
async def test_token_get(
    db: SessionDep,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Test access token
    """
    role = await db.get(Role, current_user.user_role.role_id)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "role": {
            "id": current_user.user_role.role_id,
            "name": role.name
        }
    }



@router.get("/test-customer-access")
async def test_customer_access(
    current_user: User = Security(
        deps.get_current_active_user,
        scopes=["customer"]
    )
) -> Any:
    return {
        "message": "Hello"
    }