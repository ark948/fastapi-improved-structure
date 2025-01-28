from fastapi import Depends, HTTPException, status  
from sqlalchemy.exc import IntegrityError, SQLAlchemyError  
from sqlalchemy.orm import Session  



from source.models import User
from source.schemas import user as user_schemas
from source.services.database import get_db



async def create_user_crud( payload: user_schemas.UserCreateModel, db: Session = Depends(get_db) ):
    try:
        new_user_obj = User(**payload.model_dump())
        db.add(new_user_obj)
        await db.commit()
        await db.refresh()
        
        user_data = user_schemas.UserBaseModel.model_validate(new_user_obj)
        return user_data
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(  
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
            detail=f"An error occurred while creating the property: {str(e)}",  
        )  