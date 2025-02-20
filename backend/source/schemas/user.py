from pydantic import BaseModel, ConfigDict, Field, EmailStr, UUID4
from typing import List, Optional
from enum import Enum 
from datetime import datetime



from source.models import User
from source.schemas.user_role import UserRole


class Status(Enum):  
    Success = "Success"  
    Error = "Error"  


class UserBaseModel(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "example": "Carl Johnson",
            "description": "First name and surname",
        },
    )

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class UserCreateModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    password2: str
    full_name: Optional[str] = None


class UserUpdateModel(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None



# new stuff after adding role
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str



class UserInDBBase(UserBase):
    id: UUID4
    user_role: Optional[UserRole] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class User(UserInDBBase):
    pass