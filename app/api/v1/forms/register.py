from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sql_models import db_helper

from pydantic import ValidationError
from schemas.email import EmailCheck

from cruds.user import is_email_unique, is_login_unique, create_user
from schemas import UserRegister
from utils import create_access_token
from utils import templates
from core import settings

import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(db_helper.session_getter),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):

    # Валидация
    logger.info("Валидация данных регистрации")
    if len(username) < 3 or len(username) > 24:
        logger.warning("Ошибка! Длина логина должна быть от 3 до 24 символов!")
        return templates.TemplateResponse(
            request=request,
            name="texts/wrong.html",
            context={"text": "Ошибка! Длина логина должна быть от 3 до 24 символов!"},
        )

    try:
        validation = EmailCheck(email=email)
    except ValidationError:
        logger.warning("Ошибка! Некорректный email: %r!", email=email)
        return templates.TemplateResponse(
            request=request,
            name="texts/wrong.html",
            context={"text": "Ошибка! Некорректный email!"},
        )

    if password != password_confirm:
        logger.warning("Ошибка! Пароли не совпадают!")
        return templates.TemplateResponse(
            request=request,
            name="texts/wrong.html",
            context={"text": "Ошибка! Пароли не совпадают!"},
        )

    if len(password) < 8 or len(password) > 24:
        logger.warning("Ошибка! Длина пароля должна быть от 8 до 24 символов!")
        return templates.TemplateResponse(
            request=request,
            name="texts/wrong.html",
            context={"text": "Ошибка! Длина пароля должна быть от 8 до 24 символов!"},
        )

    # Проверки на повтор

    if not await is_login_unique(session, username):
        logger.warning(
            "Ошибка! Пользователь с таким login: %r уже существует!", username
        )
        return templates.TemplateResponse(
            request=request,
            name="texts/wrong.html",
            context={"text": "Ошибка! Пользователь с таким Login уже существует!"},
        )

    if not await is_email_unique(session, email):
        logger.warning("Ошибка! Пользователь с таким email: %r уже существует!", email)
        return templates.TemplateResponse(
            request=request,
            name="texts/wrong.html",
            context={"text": "Ошибка! Пользователь с таким Email уже существует!"},
        )

    logger.info("Валидация прошла успешно")

    # Регистрация

    logger.info("Сохранение пользователя в базе данных")

    user = await create_user(
        session=session,
        user_register=UserRegister(
            login=username,
            email=email,
            password=password,
        ),
    )

    logger.info("Сохранение пользователя прошло успешно")

    logger.info("Создание токена")

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

    logger.info("Создание токена прошло успешно")

    template_response = templates.TemplateResponse(
        request=request,
        name="texts/succes.html",
        context={"text": "Аккаунт создан!"},
    )

    template_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Защита от XSS
        samesite="Strict",  # Защита от CSRF
        secure=True,  # Только HTTPS
    )

    logger.info("Регистрация прошла успешно")

    return template_response
