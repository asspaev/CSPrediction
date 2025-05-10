from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sql_models import db_helper

from utils import templates
from utils import create_access_token
from utils.predicator import Predicator
from cruds.model import get_model_by_name_and_version
from cruds.user import get_user_credits_by_email, update_user_credits_by_login, get_user_id_by_login
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

@router.post("/predict", name="PREDICT", response_class=HTMLResponse)
async def predict(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
    match_link: str = Form(...),
    model: str = Form(...),
):
    # Валидация на пустые данные
    if len(match_link) == 0:
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Не указана ссылка на матч!",
            auto_close=True,
            span='loser',
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response
    if len(model) == 0:
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Не выбрана модель!",
            auto_close=True,
            span='loser',
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response
    
    # Валидация модели
    pattern = r"(?P<name>.+?)\s+v(?P<version>[\d\.]+)\s+\((?P<price>[\d\.]+)\)"
    match = re.match(pattern, model)
    if match:
        model_info = match.groupdict()
        model_valid = await get_model_by_name_and_version(
            name=model_info['name'],
            version=model_info['version'],
            session=session,
        )
        if not model_valid:
            content = templates.get_template("popup.html").render(
                pop_up_title="Ошибка!",
                pop_up_message="Выбранная модель не найдена!",
                auto_close=True,
                span='loser',
            )
            response = HTMLResponse(content=content, status_code=200)
            response.headers["HX-Reswap"] = "none"
            return response
    else:
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Выбранная модель не найдена!",
            auto_close=True,
            span='loser',
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response

    # Валидация баланса
    access_token = request.cookies.get("access_token")
    payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
    cookie_dict = json.loads(payload.get("sub"))

    user_balance = await get_user_credits_by_email(
        email=cookie_dict['email'],
        session=session,
    )
    
    if user_balance < model_valid.price_per_prediction:
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Вам не хватает тубриков!",
            auto_close=True,
            span='loser',
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response

    # Валидация матча
    pattern = r'^https://www\.hltv\.org/matches/(\d+)/([\w-]+)$'
    match = re.match(pattern, match_link)
    if not match:
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Указана некорректная ссылка на матч!",
            auto_close=True,
            span='loser',
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response
    
    # Получение информации о матче
    try:
        response = curl_requests.get(
            url=match_link,
            impersonate="chrome",
        )
    except:
        content = templates.get_template("popup.html").render(
            pop_up_title="Ошибка!",
            pop_up_message="Не получилось найти матч, повторите попытку позже!",
            auto_close=True,
            span='loser',
        )
        response = HTMLResponse(content=content, status_code=200)
        response.headers["HX-Reswap"] = "none"
        return response
    tree = html.fromstring(response.content)
    img_src_team_1 = tree.xpath("//div[@class='team'][1]//img[contains(@class, 'logo')][1]/@src")[0]
    img_src_team_2 = tree.xpath("//div[@class='team'][2]//img[contains(@class, 'logo')][1]/@src")[0]

    if img_src_team_1[0] == "/":
        img_src_team_1 = f'https://www.hltv.org{img_src_team_1}'
    if img_src_team_2[0] == "/":
        img_src_team_2 = f'https://www.hltv.org{img_src_team_2}'

    team_name_1 = tree.xpath("//div[@class='team'][1]//div[@class='teamName'][1]/text()")[0]
    team_name_2 = tree.xpath("//div[@class='team'][2]//div[@class='teamName'][1]/text()")[0]
    match_time = tree.xpath("//div[@class='timeAndEvent'][1]//div[@class='time'][1]/text()")[0]
    match_date = tree.xpath("//div[@class='timeAndEvent'][1]//div[@class='date'][1]/text()")[0]

    path_model = f"ml_models/{model_valid.file_path}"
    with open(path_model, 'rb') as f:
        ml_model = cloudpickle.load(f)

    df_mean_player = pd.read_csv("data/mean_player.csv").drop(columns="Unnamed: 0")

    predicator = Predicator(
        model=ml_model,
        mean_player=df_mean_player,
    )

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.hltv.org/results',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"134.0.6998.189"',
        'sec-ch-ua-full-version-list': '"Chromium";v="134.0.6998.189", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.189"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"19.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Cookie': 'MatchFilter={%22active%22:false%2C%22live%22:false%2C%22stars%22:1%2C%22lan%22:false%2C%22teams%22:[]}; CookieConsent={stamp:%27vNAlTZ21gOE2NHPJPAw3r40p6OXnAr/qXvKsXt3SpEHW6R/ajmeRxw==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1742577465026%2Cregion:%27lv%27}; __cf_bm=nQjyJl3pKc3NGB0NZcOUPJCrtvz8uMKdOyUIlfYYlpE-1743823187-1.0.1.1-ojyBr7I0w7xXfmAa12B22oLjDREmG5GEeDW0iULpL7GANfg4Y95o4_lHoc5f3IF0ervwyJ.PUgzOVXWN4WUgPSr2PX49yzC4XI2X8C6ZGfY; cf_clearance=UrCu2MPi_s9nmFY8be54MwX22zG9ntXiFPUKAErQ.34-1743823189-1.2.1.1-SWUcFNWTAfd2Hauz7qMLc.tvQdstJTG2v0NewFsWQdodjPD7o501jCop2.0Ciz7iIrlnIIJfxzfkBccSERHaRdYJih8iDefzyyCF_l9SsDklwTfd081lY5UgrCa9LrWcmrOXmGoNV3SwjywHoR9IVx8VWxkwb2Avs8X0qLp.TyTxmvnwi7oj1jaBHGiRF2Mf5h7qWI.fU.Osb1mZxR6YuRgK3Hg1RcmkACRXBoLOWOxALx8MgIS0B3zmd8o85bz8CsZo6WBuYQEIWrAQ5CfOC49LdjgSkpiwbagiivF2EIX0vGUIYRDe_MM5d9X.aYoRShuy4ODSUYI3P351YFIoxn1AnH85gaQCeISSYd1GmR0'
    }
    cookies = {c.split('=')[0].strip(): c.split('=', 1)[1].strip() for c in headers["Cookie"].split('; ')}

    predicator.set_scrapp_settings(headers=headers, cookies=cookies)

    y_pred = predicator.predict(match_link)

    if y_pred[0] == 0:
        team_winner = team_name_1
        team_loser = team_name_2
    else:
        team_winner = team_name_2
        team_loser = team_name_1


    user_id = await get_user_id_by_login(session, cookie_dict['login'])

    prediction_id = await create_prediction(
        session=session,
        user_id=user_id,
        model_id=model_valid.id,
        input_text=match_link,
        team_winner=team_winner,
        team_loser=team_loser,
        credits_used=model_valid.price_per_prediction,
    )

    await create_spend(
        session=session,
        user_id=user_id,
        prediction_id=prediction_id,
        amount=model_valid.price_per_prediction,
    )

    user_balance = await get_user_credits_by_email(
        email=cookie_dict['email'],
        session=session,
    )

    new_balance = user_balance - model_valid.price_per_prediction

    await update_user_credits_by_login(
        session=session,
        login=cookie_dict['login'],
        new_credits=new_balance,
    )

    result_html = templates.get_template("utils/predict_form_result.html") \
        .render(
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

    popup_html = templates.get_template("popup.html") \
        .render(
            request=request,
            pop_up_title="Успех!",
            pop_up_message="Модель предсказала!",
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
            predict=True,
        )

    response = HTMLResponse(result_html + popup_html + header_html)

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