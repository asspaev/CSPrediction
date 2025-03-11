from fastapi import APIRouter

from core import settings

from .register import router as register_router
from .login import router as login_router
from .secret import router as secret_router


router = APIRouter()

router.include_router(
    register_router,
)
router.include_router(
    login_router,
)
router.include_router(
    secret_router,
)