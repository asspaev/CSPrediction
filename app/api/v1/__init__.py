from fastapi import APIRouter

from core import settings

from .register import router as register_router
from .login import router as login_router
from .secret import router as secret_router
from .get_balance import router as get_balance
from .deposit import router as deposit
from .get_models import router as get_models
from .predict import router as predict
from .forms import router as forms_router


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
router.include_router(
    get_balance,
    prefix=settings.api.version.balance
)
router.include_router(
    deposit,
    prefix=settings.api.version.balance
)
router.include_router(
    get_models,
    prefix=settings.api.version.models
)
router.include_router(
    predict,
    prefix=settings.api.version.models
)
router.include_router(
    forms_router,
    prefix=settings.api.version.forms
)