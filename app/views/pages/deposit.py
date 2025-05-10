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

@router.get("/deposit", name="PAGE:DEPOSIT")
async def deposit_page(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    try:

        payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
        data = json.loads(payload["sub"])

        return templates.TemplateResponse(
            request=request,
            name="pages/deposit.html",
            context={
                "title": settings.web.title,
                "login": data["login"],
                "balance_int": int(data["credits"]),
                "balance_float": '.' + str(f"{data['credits']:.2f}".split('.')[1]),
                "predict": False,
                "history_predict": False,
                "deposit": True,
                "history_balance": False,
            },
        )
    
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login")
    except jwt.PyJWTError as e:
        return RedirectResponse(url="/login")