from datetime import datetime, timedelta, timezone
from typing import Any, Union, Annotated
from fastapi import Depends, HTTPException, status, APIRouter

from source.config import settings
from source.api.deps import get_current_active_user
from jose import jwt
from passlib.context import CryptContext
from source.models import User



pwd_context = CryptContext(schemes=['pbkdf2_sha256', "bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token( subject: Union[str, Any], expires_delta: timedelta = None ) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, **subject}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)



# role must exist in both model as str, and in token
class RoleChecker:  
    def __init__(self, allowed_roles):  
        self.allowed_roles = allowed_roles
  
    def __call__(self, user: Annotated[User, Depends(get_current_active_user)]):  
        if user.role in self.allowed_roles:  
            return True  
        raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have enough permissions" )
    
# sample router to demonstrate use of RoleChecker
sample_router = APIRouter()

@sample_router.get("/data")  
async def get_data(
    _: Annotated[
        bool, Depends(
            RoleChecker(allowed_roles=["admin"])
        )
    ]
):
    print("\n", _ ,"\n")
    return {"data": "This is important data"}

