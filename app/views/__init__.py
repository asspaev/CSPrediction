from fastapi import APIRouter

from core import settings

from .auth import router as auth_router
from .pages import router as pages_router
from .favicon import router as favicon_router


router = APIRouter()

router.include_router(
    auth_router,
)
router.include_router(
    pages_router,
)
router.include_router(
    favicon_router,
)