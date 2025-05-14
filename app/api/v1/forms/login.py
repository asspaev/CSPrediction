from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sql_models import db_helper

from cruds.user import auth_user
from schemas import UserLogin
from utils import create_access_token
from utils import templates
from core import settings

import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(db_helper.session_getter),
    login: str = Form(...),
    password: str = Form(...),
):

    logging.info("Валидация данных входа")

    try:
        user = await auth_user(
            session=session,
            user_login=UserLogin(
                login=login,
                password=password,
            ),
        )
    except:
        logger.warning("Ошибка! Неверные данные для входа!")
        return templates.TemplateResponse(
            request=request,
            name="texts/wrong.html",
            context={"text": "Ошибка! Неверные данные для входа!"},
        )

    logger.info("Вход выполнен успешно")

    logger.info("Создание токена доступа")

    access_token = await create_access_token(
        data={
            "sub": json.dumps(
                {
                    "login": user.login,
                    "email": user.email,
                    "credits": user.credits,
                }
            )
        },
        private_key=settings.jwt.private,
        algorithm=settings.jwt.algorithm,
    )

    logger.info("Токен создан успешно")

    logger.info("Перенаправление на дашборд")

    response = HTMLResponse('<script>window.location.href = "/dashboard";</script>')

    logger.debug("Перенаправление выполнено успешно")

    logger.debug("Создание куки")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Защита от XSS
        samesite="Strict",  # Защита от CSRF
        secure=True,  # Только HTTPS
    )

    logger.debug("Кука создана успешно")

    return response
