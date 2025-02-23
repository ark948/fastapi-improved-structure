from fastapi import Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError  
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
import hashlib, uuid



from source.models import User
from source.services import authentication
from source.schemas import user as user_schemas
from source.schemas.user import UserBaseModel, UserCreateModel, UserUpdateModel
from source.services.database import get_db
from source.services.authentication import hash_plain_password
from source.dependencies import SessionDep
from .base import CRUDBase


async def get_user_by_id_with_role( id: str | uuid.UUID, db: SessionDep ):
    stmt = select(User).options(joinedload(User.user_role)).where( User.id == id )
    query = await db.execute( stmt )
    user = query.scalar()
    return user


async def create_user_with_role( obj_in: UserCreateModel, db: SessionDep ):
    db_obj = await User.create(
        db=db,
        email = obj_in.email,
        username = obj_in.username,
        full_name = obj_in.full_name,
        password_hash = hash_plain_password(obj_in.password),
        is_active = True
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj



async def is_user_active(user: User) -> bool:
    return user.is_active



async def crud_user_get_by_email(email: str, session: SessionDep):
    user = (await session.execute(
        select(User).where(User.email == email)
    )).scalar()
    if not user:
        return None
    return user



async def create_user_crud( payload: user_schemas.UserCreateModel, db: Session = Depends(get_db) ):
    try:
        new_user_dict = payload.model_dump()
        if not new_user_dict["password"] == new_user_dict["password2"]:
            raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match." )
        new_user_obj = await User.create(
            db=db,
            username=new_user_dict['username'],
            email=new_user_dict['email'],
            password_hash=hash_plain_password(new_user_dict['password']),
            full_name=new_user_dict['full_name']
        )
        db.add(new_user_obj)
        await db.commit()
        await db.refresh(new_user_obj)
        
        user_data = user_schemas.UserBaseModel.model_validate(new_user_obj)
        return user_data
    
    except IntegrityError as integ_error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"error: {str(integ_error)}"
        )
    
    except SQLAlchemyError as sql_error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"sqlalchemy error: {str(sql_error)}"
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(  
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
            detail=f"An error occurred while creating the property: {str(e)}",  
        )
    

async def activate_user_crud( user: User, db: SessionDep ):
    try:
        user.is_active = True
        await db.commit()
        return True

    except IntegrityError as integ_error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"error: {str(integ_error)}"
        )
    
    except SQLAlchemyError as sql_error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"sqlalchemy error: {str(sql_error)}"
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(  
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
            detail=f"An error occurred while creating the property: {str(e)}",  
        )
    


class CRUDUser(CRUDBase[User, UserCreateModel, UserUpdateModel]):
    async def get( self, db: AsyncSession, obj_id: str) -> User:
        return await super().get(db, obj_id)
    
    async def get_or_create(self, db: AsyncSession, defaults: Dict[str, Any] | None, **kwargs: Any) ->  User:
        return await super().get_or_create(db, defaults, **kwargs)
    
    # -> Page[Product]
    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 20) -> Any:
        return await super().get_multi(db, skip=skip, limit=limit)

    def get_multi( self, db: AsyncSession, *, skip: int = 0, limit: int = 100, ) -> List[User]:
        return db.query(self.model).offset(skip).limit(limit).all()

    async def update(self, db: AsyncSession, *, obj_current: User, obj_new: UserUpdateModel | Dict[str, Any] | User):
        return await super().update(db, obj_current=obj_current, obj_new=obj_new)

    async def remove(self, db: AsyncSession, *, obj_id: str) -> User | None:
        return await super().remove(db, obj_id=obj_id)
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        # return await db.query(self.model).filter(User.email == email).first()
        stmt = select(User).options(joinedload(User.user_role)).where(User.email == email)
        query = await db.execute(stmt)
        user = query.scalar()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User with this email was not found.",
            )
        return user
    
    async def authenticate( self, db: AsyncSession, *, email: str, password: str ) -> Optional[User]:
        user: User = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not authentication.verify_password(password, user.password_hash):
            return None
        return user
    

user_crud = CRUDUser(User)