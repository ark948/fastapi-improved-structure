from typing import Any, List

from source.constants import role as role_const
from source.schemas import role as role_schemas
from source.api import deps
from fastapi import Security
from source.models import User
from source.crud import role as role_crud
from source.api import deps
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession
from source.dependencies import SessionDep



router = APIRouter()


@router.get("/", response_model=List[role_schemas.Role])
async def get_roles(
    db: SessionDep, skip: int = 0, limit: int = 100,
) -> Any:
    """
    Retrieve all available user roles.
    """
    roles = await role_crud.role.get_multi(db ,skip=skip, limit=limit)
    return roles



@router.post("/", response_model=role_schemas.RoleInDB)
async def create( 
    role_in: role_schemas.RoleCreate, 
    db: SessionDep,
    current_user: User = Security( deps.get_current_active_user )
) -> role_schemas.Role:
    role = await role_crud.role.create(db, obj_in=role_in)
    return role




@router.post("/open", response_model=role_schemas.RoleInDB)
async def create_open(
    role_in: role_schemas.RoleCreate,
    db: SessionDep,
    current_user: User = Security( deps.get_current_user )
) -> Any:
    try:
        role = await role_crud.role.create(db, obj_in=role_in)
    except Exception as error:
        print("ERROR -> ", str(error))
        return None
    return role
    