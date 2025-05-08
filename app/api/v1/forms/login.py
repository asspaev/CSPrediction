from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sql_models import db_helper

from pydantic import ValidationError
from schemas.email import EmailCheck

from cruds.user import is_email_unique, is_login_unique, auth_user
from schemas import UserLogin
from utils import create_access_token
from utils import templates
from core import settings

router = APIRouter()

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(db_helper.session_getter),
    login: str = Form(...),
    password: str = Form(...),
):
    
    try:
        user = await auth_user(
            session=session,
            user_login=UserLogin(
                login=login,
                password=password,
            ),
        )
    except:
        return templates.TemplateResponse(
            request=request,
            name="texts/wrong.html",
            context={
                "text": "Ошибка! Неверные данные для входа!"
            },
        )

    access_token = await create_access_token(
        data={"sub": {
                "login": user.login,
                "email": user.email,
            }
        },
        private_key=settings.jwt.private,
        algorithm=settings.jwt.algorithm,
        )
    
    template_response = templates.TemplateResponse(
        request=request,
        name="texts/succes.html",
        context={
            "text": "Авторизация успешно прошла!!"
        },
    )

    template_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Защита от XSS
        samesite="Strict",  # Защита от CSRF
        secure=True  # Только HTTPS
    )

    return template_response