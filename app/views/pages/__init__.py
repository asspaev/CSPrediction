from fastapi import APIRouter

from core import settings

from .dashboard import router as dashboard_router
from .predict import router as predict_router
from .history_predict import router as history_predict_router
from .deposit import router as deposit_router
from .history_balance import router as history_balance_router


router = APIRouter()

router.include_router(
    dashboard_router,
)
router.include_router(
    predict_router,
)
router.include_router(
    history_predict_router,
)
router.include_router(
    deposit_router,
)
router.include_router(
    history_balance_router,
)