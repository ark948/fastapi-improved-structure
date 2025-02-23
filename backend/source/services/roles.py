from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List



# NOTE this entire module is not used



# this is just for demonstration
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def check_roles(roles: List[str]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get the current user's roles from the database or token
            # Check if any of the roles match the required roles
            # If not, raise an HTTPException with 403 status code
            # Else, continue with the execution of the function
            return func(*args, **kwargs)
        return wrapper
    return decorator


@router.get("/protected_route")
@check_roles(["admin"])
def protected_route():
    return {"message": "You have access to this protected route!"}