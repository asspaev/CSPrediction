from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/", name="INDEX")
async def index_page(
    request: Request,
):
    return RedirectResponse(url="/dashboard")
