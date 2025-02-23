from typing import Optional

from source.crud.base import CRUDBase
from source.models import UserRole
from source.schemas.user_role import UserRoleCreate, UserRoleUpdate
from pydantic.types import UUID4
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession


class CRUDUserRole(CRUDBase[UserRole, UserRoleCreate, UserRoleUpdate]):
    async def get_by_user_id( self, db: AsyncSession, *, user_id: UUID4 | str ) -> Optional[UserRole]:
        return db.query(UserRole).filter(UserRole.user_id == user_id).first()


user_role = CRUDUserRole(UserRole)