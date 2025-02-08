from fastapi import Depends, HTTPException, status  
from sqlalchemy.exc import IntegrityError, SQLAlchemyError  
from sqlalchemy.orm import Session
import hashlib, uuid



from source.models import User
from source.schemas import user as user_schemas
from source.services.database import get_db
from source.services.authentication import hash_plain_password
from source.dependencies import SessionDep



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
    