from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.auth.router import router as auth_router
from src.lib.database import engine
from src.lib.exceptions import (
    AppException,
    ErrorDetail,
    ErrorResponse,
    make_error_response,
)
from src.lib.redis import redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await redis.aclose()
    await engine.dispose()


app = FastAPI(
    title="Globe CRM API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return make_error_response(exc)


app.include_router(auth_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
