from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from core.config import settings


app = FastAPI(
    default_response_class=ORJSONResponse,
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )