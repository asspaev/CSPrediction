from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sql_models import db_helper

from cruds.model import get_model_by_name_and_version
from utils import templates

import re

router = APIRouter()

@router.post("/price_model", name="PRICE_MODEL", response_class=HTMLResponse)
async def price_model(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
    model: str = Form(...),
):
    
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
            return None
    else:
        return None

    return templates.TemplateResponse(
        request=request,
        name="texts/model_cost.html",
        context={
            "model_price": model_valid.price_per_prediction, 
            "model_exist": True,
        },
    )