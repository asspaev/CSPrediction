from fastapi import APIRouter

from core import settings

from .auth import router as auth_router


router = APIRouter()

router.include_router(
    auth_router,
)