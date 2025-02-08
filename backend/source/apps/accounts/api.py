from typing import Annotated, Dict, Union
from fastapi import APIRouter, Depends, status, HTTPException, Body, Request, Header
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates


from source.services.database import get_db
from source.models import User
from source.schemas import user as user_schemas
from source.crud import user as user_crud
from source.services.authentication import AuthDep, get_current_user
from source import utils
from source.services.redis import submit_otp_for_user, verify_otp_for_user, RedisDep
from source.dependencies import SessionDep
from source.utils import myprint




router = APIRouter()
templates = Jinja2Templates(directory='templates')



@router.get('/test', response_model=str, status_code=200)
async def test():
    return 'ok'



@router.get('/html-test', response_class=HTMLResponse | JSONResponse)
async def html_test(request: Request):
    
    if request.headers["accept"].split(',')[0] == 'text/html':
        print("HTML Response")
        return templates.TemplateResponse(
            request=request, name='test.html', context={"message": "Hello from fastapi"}
        )
    elif request.headers["accept"].split(',')[0] == 'text/json':    
            print("JSON Response")
            return JSONResponse(
                content={"message": "hey"}
            )
    else:
        raise HTTPException(
            status_code=500,
            detail="Unable to render response."
        )