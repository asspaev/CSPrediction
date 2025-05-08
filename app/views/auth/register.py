from fastapi import APIRouter, Request

from utils import templates

from core.config import settings

router = APIRouter()

@router.get("/register", name="AUTH:REGISTER")
async def register_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={
            "title": settings.web.title,
            "register_api": f"{settings.api.prefix}{settings.api.version.prefix}{settings.api.version.forms}/register",
        },
    )