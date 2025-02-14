from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import List, Optional
from enum import Enum 



from source.models import User


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
