from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession
from source.services.database import get_db




SessionDep = Annotated[AsyncSession, Depends(get_db)]
