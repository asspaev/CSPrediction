from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Dict

from core import settings
from sql_models import db_helper
from schemas import UserRegister
from utils import create_access_token
from cruds.user import create_user


router = APIRouter()


@router.post("/register")
async def register(
    data: UserRegister,
    response: Response,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Dict[str, str]:
    user = await create_user(
        session=session,
        user_register=data,
    )
    access_token = await create_access_token(
        data={"sub": data.email},
        private_key=settings.jwt.private,
        algorithm=settings.jwt.algorithm,
        )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Защита от XSS
        samesite="Strict",  # Защита от CSRF
        secure=True  # Только HTTPS
    )
    return {"message": "Вы удачно зарегистрировались!"}