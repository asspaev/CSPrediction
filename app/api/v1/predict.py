from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    Request,
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import joblib

from typing import Dict

from core import settings
from sql_models import db_helper
from schemas import Predict
from utils import Predicator
from cruds.model import get_model_by_id


router = APIRouter()


@router.post("/predict")
async def predict(
    data: Predict,
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не авторизированы!")
    try:

        payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
        model = await get_model_by_id(data.model_id, session)
        if not model:
            raise HTTPException(status_code=404, detail=f"Модель под номер '{data.model_id}' не найдена.")
        else:

            path_save = settings.predict.path_dir_models / model.file_path
            model = joblib.load(path_save)

            predicator = Predicator(
                model=model,
                mean_player=settings.predict.mean_player,
            )

            predicator.set_scrapp_settings(
                headers=settings.predict.headers, 
                cookies=settings.predict.cookies,
            )

            y_pred = predicator.predict(data.match_link)
            return {"result": y_pred}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истёк. Авторизируйтесь заново.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Ваш токен недействителен. Авторизируйтесь заново.")