from fastapi import APIRouter

from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/images/favicon_ai.svg")
