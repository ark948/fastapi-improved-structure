from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from source.services.database import get_db




SessionDep = Annotated[Session, Depends(get_db)]
