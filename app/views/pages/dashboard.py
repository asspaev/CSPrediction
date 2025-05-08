from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from utils import templates

from core import settings
import jwt

import json

router = APIRouter()

@router.get("/dashboard", name="PAGE:DASHBOARD")
async def dashboard_page(
    request: Request,
):
    
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    try:

        payload = jwt.decode(access_token, settings.jwt.public, algorithms=[settings.jwt.algorithm])
        data = json.loads(payload["sub"])

        return templates.TemplateResponse(
            request=request,
            name="pages/loading.html",
            context={
                "title": settings.web.title,
                "login": data["login"],
                "balance_int": int(data["credits"]),
                "balance_float": '.' + str(f"{data['credits']:.2f}".split('.')[1]),
                "logout_link": f"{settings.api.prefix}{settings.api.version.prefix}/logout",
            },
        )
    
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login")
    except jwt.PyJWTError as e:
        return RedirectResponse(url="/login")
    
    