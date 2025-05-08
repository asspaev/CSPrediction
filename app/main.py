from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from contextlib import asynccontextmanager

from api import router
from core import settings
from sql_models import (
    db_helper,
    Base,
)


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print('dispose engine')
    await db_helper.dispose()

app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(
    router,
    prefix=settings.api.prefix,
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )