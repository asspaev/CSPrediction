from fastapi import APIRouter

from core import settings

from .dashboard import router as dashboard_router


router = APIRouter()

router.include_router(
    dashboard_router,
)