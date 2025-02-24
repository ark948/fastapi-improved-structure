from typing import Optional

from source.crud.base import CRUDBase
from source.models import UserRole
from source.schemas.user_role import UserRoleCreate, UserRoleUpdate
from pydantic.types import UUID4
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select



class CRUDUserRole(CRUDBase[UserRole, UserRoleCreate, UserRoleUpdate]):
    async def get_by_user_id( self, db: AsyncSession, *, user_id: UUID4 | str ) -> Optional[UserRole]:
        return db.query(UserRole).filter(UserRole.user_id == user_id).first()
    
    async def get_user_role_by_user_id( self, db: AsyncSession, *, user_id: UUID4 | str ) -> Optional[UserRole]:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        query = await db.execute(stmt)
        user_role = query.scalar()
        if not user_role:
            return None
        return user_role


user_role = CRUDUserRole(UserRole)