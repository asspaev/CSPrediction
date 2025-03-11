from fastapi import APIRouter

from core import settings

from .register import router as register_router


router = APIRouter()

router.include_router(
    register_router,
)