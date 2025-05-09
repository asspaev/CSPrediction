from fastapi import APIRouter

from core import settings

from .forms import router as forms_router
from .logout import router as logout_router
from .popup import router as popup_router


router = APIRouter()

router.include_router(
    forms_router,
    prefix=settings.api.version.forms
)
router.include_router(
    logout_router,
)
router.include_router(
    popup_router,
)