from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    Request,
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from typing import Dict

from core import settings
from sql_models import db_helper
from schemas import UserLogin
from utils import create_access_token
from cruds.user import auth_user


router = APIRouter()


@router.get("/protected")
async def read_protected(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не авторизированы!")
    try:
        payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
        return {"message": "Вам доступна секретная страница!", "user": payload["sub"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истёк. Авторизируйтесь заново.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Ваш токен недействителен. Авторизируйтесь заново.")