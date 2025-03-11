from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from core import settings
from models import db_helper
from schemas import UserRegister
from utils import create_access_token
from servises.user import create_user


router = APIRouter()


@router.post("/register")
async def register(
    data: UserRegister,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await create_user(
        session=session,
        user_register=data,
    )
    access_token = await create_access_token(
        data={"sub": data.email},
        private_key=settings.jwt.private,
        algorithm=settings.jwt.algorithm,
        )
    return {"access_token": access_token, "token_type": settings.auth.token_type}