from typing import Annotated, Dict, Union
from fastapi import APIRouter, Depends, status, HTTPException, Body, Request, Header, Form
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates


from source.services.database import get_db
from source.models import User
from source.schemas import user as schemas
from source.crud import user as user_crud
from source.services.authentication import AuthDep, get_current_user
from source import utils
from source.services.redis import submit_otp_for_user, verify_otp_for_user, RedisDep
from source.dependencies import SessionDep
from source.utils import myprint




pages_router = APIRouter()
acc_router = APIRouter()
templates = Jinja2Templates(directory='templates')

@pages_router.get('/register', response_class=HTMLResponse)
async def load_register_page(request: Request):
    return templates.TemplateResponse(request=request, name='accounts/register.html')

@acc_router.post('/register', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def register(
        request: Request, db: SessionDep,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        password2: str = Form(...),
        full_name: str = Form(...)
    ):
    if password != password2:
         return HTMLResponse(content="<p>Passwords do not match.</p>", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    payload = schemas.UserCreateModel(username=username, email=email, password=password, password2=password2, full_name=full_name)
    try:
        resposne = await user_crud.create_user_crud(payload, db)
        if resposne:
            return templates.TemplateResponse(request=request, name='accounts/register.html', context={'message': "Registration successful."})
    except Exception as error:
        myprint(error)
        return HTMLResponse(content="<p>Registration failed. Please check your input. </p>", status_code=status.HTTP_409_CONFLICT)