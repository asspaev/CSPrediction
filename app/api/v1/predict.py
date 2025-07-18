from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse

from starlette.concurrency import run_in_threadpool

from sqlalchemy.ext.asyncio import AsyncSession
from sql_models import db_helper

from utils import templates
from utils import create_access_token
from cruds.model import get_model_by_name_and_version
from cruds.spend import create_spend
from cruds.prediction import create_prediction
from cruds.user import (
    update_user_credits_by_login,
    get_user_id_by_login,
    get_user_credits_by_email,
)

from core import settings

from lxml import html
from curl_cffi import requests as curl_requests

import re
import json
import jwt

from tasks import task_predict

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", name="PREDICT", response_class=HTMLResponse)
async def predict(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
    match_link: str = Form(...),
    model: str = Form(...),
):

    logger.info("Валидация данных предсказания")

    # Валидация на пустые данные
    if len(match_link) == 0:
        logger.warning("Ошибка! Не указана ссылка на матч!")
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Не указана ссылка на матч!",
            auto_close=True,
            span="loser",
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response
    if len(model) == 0:
        logger.warning("Ошибка! Не выбрана модель!")
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Не выбрана модель!",
            auto_close=True,
            span="loser",
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response

    logger.info("Валидация данных предсказания завершена")

    logger.info("Валидация модели")

    # Валидация модели
    pattern = r"(?P<name>.+?)\s+v(?P<version>[\d\.]+)\s+\((?P<price>[\d\.]+)\)"
    match = re.match(pattern, model)
    if match:
        model_info = match.groupdict()
        model_valid = await get_model_by_name_and_version(
            name=model_info["name"],
            version=model_info["version"],
            session=session,
        )
        if not model_valid:
            logger.warning("Ошибка! Выбранная модель не найдена!")
            content = templates.get_template("popup.html").render(
                pop_up_title="Ошибка!",
                pop_up_message="Выбранная модель не найдена!",
                auto_close=True,
                span="loser",
            )
            response = HTMLResponse(content=content, status_code=200)
            response.headers["HX-Reswap"] = "none"
            return response
    else:
        logger.warning("Ошибка! Выбранная модель не найдена!")
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Выбранная модель не найдена!",
            auto_close=True,
            span="loser",
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response

    logger.info("Валидация модели завершена")

    logger.info("Валидация баланса")

    # Валидация баланса
    access_token = request.cookies.get("access_token")
    payload = jwt.decode(
        access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm]
    )
    cookie_dict = json.loads(payload.get("sub"))

    user_balance = await get_user_credits_by_email(
        email=cookie_dict["email"],
        session=session,
    )

    if user_balance < model_valid.price_per_prediction:
        logger.warning("Ошибка! Не хватает тубриков!")
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Вам не хватает тубриков!",
            auto_close=True,
            span="loser",
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response

    logger.info("Валидация баланса завершена")

    logger.info("Валидация матча")

    # Валидация матча
    pattern = r"^https://www\.hltv\.org/matches/(\d+)/([\w-]+)$"
    match = re.match(pattern, match_link)
    if not match:
        logger.warning("Ошибка! Указана некорректная ссылка на матч!")
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Указана некорректная ссылка на матч!",
            auto_close=True,
            span="loser",
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response

    logger.info("Валидация матча завершена")

    logger.info("Получение информации о матче")

    # Получение информации о матче
    try:
        response = curl_requests.get(
            url=match_link,
            impersonate="chrome",
        )
    except:
        logger.warning("Ошибка! Не получилось найти матч!")
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Не получилось найти матч, повторите попытку позже!",
            auto_close=True,
            span="loser",
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response

    logger.info("Получение информации о матче завершено")

    logger.info("Парсинг информации о матче")

    tree = html.fromstring(response.content)
    img_src_team_1 = tree.xpath(
        "//div[@class='team'][1]//img[contains(@class, 'logo')][1]/@src"
    )[0]
    img_src_team_2 = tree.xpath(
        "//div[@class='team'][2]//img[contains(@class, 'logo')][1]/@src"
    )[0]

    if img_src_team_1[0] == "/":
        img_src_team_1 = f"https://www.hltv.org{img_src_team_1}"
    if img_src_team_2[0] == "/":
        img_src_team_2 = f"https://www.hltv.org{img_src_team_2}"

    team_name_1 = tree.xpath(
        "//div[@class='team'][1]//div[@class='teamName'][1]/text()"
    )[0]
    team_name_2 = tree.xpath(
        "//div[@class='team'][2]//div[@class='teamName'][1]/text()"
    )[0]
    match_time = tree.xpath(
        "//div[@class='timeAndEvent'][1]//div[@class='time'][1]/text()"
    )[0]
    match_date = tree.xpath(
        "//div[@class='timeAndEvent'][1]//div[@class='date'][1]/text()"
    )[0]

    logger.info(
        "Парсинг информации о матче завершен, team_name_1: %r, team_name_2: %r, match_time: %r, match_date: %r",
        team_name_1,
        team_name_2,
        match_time,
        match_date,
    )

    logger.info("Отправление таска на предсказание")

    # Predict
    path_model = f"ml_models/{model_valid.file_path}"
    predict = task_predict.delay(
        path_model=path_model,
        match_link=match_link,
    )
    predict = await run_in_threadpool(predict.get, 300)

    logger.info("Ответ предсказания модели: %r", predict)

    if predict == 0:
        team_winner = team_name_1
        team_loser = team_name_2
    else:
        team_winner = team_name_2
        team_loser = team_name_1

    user_id = await get_user_id_by_login(session, cookie_dict["login"])

    logger.info("Сохранение предсказания в БД")

    prediction_id = await create_prediction(
        session=session,
        user_id=user_id,
        model_id=model_valid.id,
        input_text=match_link,
        team_winner=team_winner,
        team_loser=team_loser,
        credits_used=model_valid.price_per_prediction,
    )

    logger.info("Сохранение предсказания в БД завершено")

    logger.info("Сохранение расхода в БД")

    await create_spend(
        session=session,
        user_id=user_id,
        prediction_id=prediction_id,
        amount=model_valid.price_per_prediction,
    )

    logger.info("Сохранение расхода в БД завершено")

    user_balance = await get_user_credits_by_email(
        email=cookie_dict["email"],
        session=session,
    )

    new_balance = user_balance - model_valid.price_per_prediction

    await update_user_credits_by_login(
        session=session,
        login=cookie_dict["login"],
        new_credits=new_balance,
    )

    result_html = templates.get_template("utils/predict_form_result.html").render(
        request=request,
        img_team_1=img_src_team_1,
        img_team_2=img_src_team_2,
        team_name_1=team_name_1,
        team_name_2=team_name_2,
        match_time=match_time,
        match_date=match_date,
        team_winner=team_winner,
        team_loser=team_loser,
        balance_int=123,
    )

    popup_html = templates.get_template("popup.html").render(
        request=request,
        pop_up_title="Успех!",
        pop_up_message="Модель предсказала!",
        auto_close=True,
        span="winner",
    )

    header_html = templates.get_template("header.html").render(
        request=request,
        title=settings.web.title,
        login=cookie_dict["login"],
        balance_int=int(new_balance),
        balance_float="." + str(f"{new_balance:.2f}".split(".")[1]),
        predict=True,
    )

    response = HTMLResponse(result_html + popup_html + header_html)

    access_token = await create_access_token(
        data={
            "sub": json.dumps(
                {
                    "login": cookie_dict["login"],
                    "email": cookie_dict["email"],
                    "credits": new_balance,
                }
            )
        },
        private_key=settings.jwt.private,
        algorithm=settings.jwt.algorithm,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Защита от XSS
        samesite="Strict",  # Защита от CSRF
        secure=True,  # Только HTTPS
    )

    return response
