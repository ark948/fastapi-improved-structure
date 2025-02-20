from fastapi import FastAPI, HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from passlib.context import CryptContext
from typing import Annotated, Union, Dict
import jwt #pip install pyjwt
from jwt import InvalidTokenError
import threading
import time
from datetime import datetime, timezone, timedelta



from source.config import settings
from source.dependencies import SessionDep
from source.models import User




SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")




class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None



async def get_user_from_email(email: str, session: SessionDep) -> User:
    user = (await session.execute(
        select(User).where(User.email == email)
    )).scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User with this email was not found.",
        )
    return user
    


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_plain_password(password) -> str:
    return pwd_context.hash(password)


async def get_user(email: str, session: SessionDep):
    return await get_user_from_email(email, session)



def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(email=token_data.email, session=session)
    if user is None:
        raise credentials_exception
    return user



async def authenticate_user(email: str, password: str, session: SessionDep):
    user = await get_user(email=email, session=session)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user



# form-data requires --> pip install python-multipart
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_for_access_token( form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep ) -> Token:
    user = await authenticate_user(email=form_data.username, password=form_data.password, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    token = Token(access_token=access_token, token_type="bearer")
    return token



AuthDep = Annotated[User, Depends(get_current_user)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]