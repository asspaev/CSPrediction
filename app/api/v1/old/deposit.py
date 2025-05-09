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
from schemas import Deposit
from utils import create_access_token
from cruds.user import get_user_credits_by_email, add_credits_by_email


router = APIRouter()


@router.post("/deposit")
async def deposit(
    data: Deposit,
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не авторизированы!")
    try:

        payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
        await add_credits_by_email(
            email=payload["sub"],
            amount=data.deposit,
            session=session,
        )
        credits = await get_user_credits_by_email(payload["sub"], session)
        return {"balance": credits}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истёк. Авторизируйтесь заново.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Ваш токен недействителен. Авторизируйтесь заново.")