from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from utils import templates
from sql_models import db_helper
from cruds.prediction import get_predictions_by_login
from core import settings

import jwt
import json

router = APIRouter()

@router.get("/history_predict", name="PAGE:HISTORY_PREDICT")
async def history_predict_page(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    try:

        payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
        data = json.loads(payload["sub"])

        predictions = await get_predictions_by_login(
            session=session,
            login=data["login"],
        )
        predictions = [
            {
            "id": prediction.id, 
            "date": prediction.created_at, 
            "link": prediction.input_text, 
            "winner": prediction.team_winner, 
            "loser": prediction.team_loser, 
            "model": f"{prediction.model.name} v{prediction.model.version}", 
            "price_int": int(prediction.credits_used), 
            "price_float": '.' + str(f"{prediction.credits_used:.2f}".split('.')[1]), 
            }
            for prediction in predictions
        ]

        return templates.TemplateResponse(
            request=request,
            name="pages/history_predict.html",
            context={
                "title": settings.web.title,
                "login": data["login"],
                "balance_int": int(data["credits"]),
                "balance_float": '.' + str(f"{data['credits']:.2f}".split('.')[1]),
                "predict": False,
                "history_predict": True,
                "deposit": False,
                "history_balance": False,
                "predictions": predictions[::-1],
            },
        )
    
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login")
    except jwt.PyJWTError as e:
        return RedirectResponse(url="/login")
    
    