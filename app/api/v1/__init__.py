from fastapi import APIRouter

from core import settings

from .forms import router as forms_router
from .logout import router as logout_router
from .popup import router as popup_router
from .price_model import router as price_model_router
from .predict import router as predict_router
from .deposit import router as deposit_router


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
router.include_router(
    price_model_router,
)
router.include_router(
    predict_router,
)
router.include_router(
    deposit_router,
)