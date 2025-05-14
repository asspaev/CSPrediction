from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from contextlib import asynccontextmanager

from api import api_router as api_router
from views import router as views_router
from core import settings
from sql_models import (
    db_helper,
    Base,
)

from utils import configure_logging
import logging

configure_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # здесь запускается FastAPI

    logger.info("Dispose engine complete")
    await db_helper.dispose()


app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(
    api_router,
    prefix=settings.api.prefix,
)

app.include_router(
    views_router,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    logger.info("Start app")
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
