from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from utils import templates
from sql_models import db_helper
from cruds.model import get_all_models

from core import settings
import jwt

import json

router = APIRouter()


@router.get("/dashboard", name="PAGE:DASHBOARD")
async def dashboard_page(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):

    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    try:

        payload = jwt.decode(
            access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm]
        )
        data = json.loads(payload["sub"])

        models = await get_all_models(session=session)
        models = [
            {
                "name": model.name,
                "version": model.version,
                "price": model.price_per_prediction,
            }
            for model in models
        ]

        return templates.TemplateResponse(
            request=request,
            name="pages/predict.html",
            context={
                "title": settings.web.title,
                "predict": True,
                "login": data["login"],
                "balance_int": int(data["credits"]),
                "balance_float": "." + str(f"{data['credits']:.2f}".split(".")[1]),
                "models": models,
            },
        )

    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login")
    except jwt.PyJWTError as e:
        return RedirectResponse(url="/login")
