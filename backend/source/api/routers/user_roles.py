from typing import Any

from source import models
from source.crud import user_role as user_role_crud
from source.models import User
from source.schemas import user_role as user_role_schemas
from source.api import deps
from source.constants.role import Role
from fastapi import APIRouter, Depends, HTTPException, Security
from pydantic.types import UUID4
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession
from source.dependencies import SessionDep
from source.services.database import get_db



router = APIRouter()


@router.post("", response_model=user_role_schemas.UserRoleBase)
async def assign_user_role(
    *,
    db: AsyncSession = Depends(get_db),
    user_role_in: user_role_schemas.UserRoleCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Assign a role to a user after creation of a user
    """
    user_role = await user_role_crud.user_role.get_user_role_by_user_id( db, user_id=user_role_in.user_id )
    if user_role:
        raise HTTPException(
            status_code=409,
            detail="This user has already been assigned a role.",
        )
    user_role = await user_role_crud.user_role.create( db, obj_in=user_role_in )
    return user_role


@router.put("/{user_id}", response_model=user_role_schemas.UserRole)
async def update_user_role(
    *,
    db: Session = Depends(get_db),
    user_id: UUID4 | str,
    user_role_in: user_role_schemas.UserRoleUpdate,
    current_user: User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.SUPER_ADMIN["name"],
            Role.ACCOUNT_ADMIN["name"],
        ],
    ),
) -> Any:
    """
    Update a users role.
    """
    user_role = await user_role_crud.user_role.get_by_user_id(db, user_id=user_id)
    if not user_role:
        raise HTTPException(
            status_code=404, detail="There is no role assigned to this user",
        )
    
    user_role = await user_role_crud.user_role.update( db, obj_current=user_role, obj_new=user_role_in )
    return user_role