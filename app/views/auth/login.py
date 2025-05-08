from fastapi import APIRouter, Request

from utils import templates

from core.config import settings

router = APIRouter()

@router.get("/login", name="AUTH:LOGIN")
async def login_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "title": settings.web.title,
            "login_api": f"{settings.api.prefix}{settings.api.version.prefix}{settings.api.version.forms}/login",
        },
    )