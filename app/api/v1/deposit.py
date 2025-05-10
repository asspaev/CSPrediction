from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sql_models import db_helper

from utils import templates
from utils import create_access_token
from utils.predicator import Predicator
from cruds.model import get_model_by_name_and_version
from cruds.user import get_user_credits_by_email, update_user_credits_by_login, get_user_id_by_login
from cruds.deposit import add_deposit
from cruds.spend import create_spend
from cruds.prediction import create_prediction

from core import settings

from lxml import html
from curl_cffi import requests as curl_requests

import re
import json
import jwt
import pandas as pd
import cloudpickle

router = APIRouter()

@router.post("/deposit", name="DEPOSIT", response_class=HTMLResponse)
async def deposit(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
    deposit = Form(...),
):
    # Валидация на пустые данные
    if not deposit:
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Введите количество для пополнения!",
            auto_close=True,
            span='loser',
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response
    
    # Валидация на минус
    if float(deposit) <= 0:
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Введите значение больше нуля!",
            auto_close=True,
            span='loser',
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response
    
    access_token = request.cookies.get("access_token")
    payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
    cookie_dict = json.loads(payload.get("sub"))

    user_balance = await get_user_credits_by_email(
        email=cookie_dict['email'],
        session=session,
    )

    new_balance = user_balance + float(deposit)

    await update_user_credits_by_login(
        session=session,
        login=cookie_dict['login'],
        new_credits=new_balance,
    )

    user_id = await get_user_id_by_login(session, cookie_dict['login'])

    await add_deposit(
        session=session,
        user_id=user_id,
        amount=float(deposit),
    )

    popup_html = templates.get_template("popup.html") \
        .render(
            request=request,
            pop_up_title="Пополнение!",
            pop_up_message="Баланс успешно пополнен!",
            auto_close=True,
            span='winner',
        )
    
    header_html = templates.get_template("header.html") \
        .render(
            request=request,
            title=settings.web.title,
            login=cookie_dict["login"],
            balance_int=int(new_balance),
            balance_float='.' + str(f"{new_balance:.2f}".split('.')[1]),
            deposit=True,
        )

    response = HTMLResponse("Пополнить баланс" + popup_html + header_html)

    access_token = await create_access_token(
        data={"sub": json.dumps({
                "login": cookie_dict["login"],
                "email": cookie_dict["email"],
                "credits": new_balance,
            })
        },
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
    
    return response