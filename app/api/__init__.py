from fastapi import APIRouter

from core import settings

from .v1 import router as v1_router


router = APIRouter()

router.include_router(
    v1_router,
    prefix=settings.api.v1.prefix,
)