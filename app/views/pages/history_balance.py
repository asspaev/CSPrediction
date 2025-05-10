from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from utils import templates
from sql_models import db_helper
from cruds.multiple import get_user_transactions
from cruds.user import get_user_id_by_login
from core import settings

import jwt
import json

router = APIRouter()

@router.get("/history_balance", name="PAGE:HISTORY_BALANCE")
async def history_balance_page(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    try:

        payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
        data = json.loads(payload["sub"])

        user_id = await get_user_id_by_login(
            session=session,
            login=data["login"],
        )

        transactions = await get_user_transactions(
            session=session,
            user_id=user_id,
        )

        return templates.TemplateResponse(
            request=request,
            name="pages/history_balance.html",
            context={
                "title": settings.web.title,
                "login": data["login"],
                "balance_int": int(data["credits"]),
                "balance_float": '.' + str(f"{data['credits']:.2f}".split('.')[1]),
                "predict": False,
                "history_predict": False,
                "deposit": False,
                "history_balance": True,
                "transactions": transactions,
            },
        )
    
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login")
    except jwt.PyJWTError as e:
        return RedirectResponse(url="/login")
    
    