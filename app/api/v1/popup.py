from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from utils import templates

router = APIRouter()

@router.post("/popup", name="NEW_POPUP", response_class=HTMLResponse)
async def popup(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="popup.html",
        context={
            "pop_up_title": "Уведомление", 
            "pop_up_message": "Ссылка успешно скопирована!",
            "auto_close": True,
        },
    )