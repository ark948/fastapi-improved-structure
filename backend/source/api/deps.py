from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi import Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio.session import AsyncSession
from pydantic import ValidationError
from jose import jwt


from source.constants.role import Role
from source.crud.user import is_user_active
from source.models import User
from source.services.database import get_db
from source.config import settings
from source.schemas.token import TokenPayload



# oatuh2 scope format example: users:write or users:read

ALGORITHM = "HS256"

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/auth/access-token",
    scopes={
        Role.GUEST["name"]: Role.GUEST["description"],
        Role.ACCOUNT_ADMIN["name"]: Role.ACCOUNT_ADMIN["description"],
        Role.ACCOUNT_MANAGER["name"]: Role.ACCOUNT_MANAGER["description"],
        Role.ADMIN["name"]: Role.ADMIN["description"],
        Role.SUPER_ADMIN["name"]: Role.SUPER_ADMIN["description"],
    },
)



async def get_current_user( 
        security_scopes: SecurityScopes, db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2),
    ) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode( token, settings.SECRET_KEY, algorithms=[ALGORITHM] )
        if payload.get("id") is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        # logger.error("Error Decoding Token", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = User.get(db, id=token_data.id)
    if not user:
        raise credentials_exception
    if security_scopes.scopes and not token_data.role:
        raise HTTPException(
            status_code=401,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    if ( security_scopes.scopes and token_data.role not in security_scopes.scopes ):
        raise HTTPException(
            status_code=401,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return user



def get_current_active_user( current_user: User = Security(get_current_user, scopes=[], ), ) -> User:
    if not is_user_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user