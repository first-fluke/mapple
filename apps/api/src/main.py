import os
from collections.abc import AsyncGenerator, Awaitable
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.auth.router import router as auth_router
from src.contact_relationships.router import router as contact_relationships_router
from src.contacts.router import router as contacts_router
from src.experiences.router import router as experiences_router
from src.export.router import router as export_router
from src.geocoding.router import router as geocoding_router
from src.globe.router import router as globe_router
from src.graph.router import router as graph_router
from src.imports.router import router as imports_router
from src.lib.database import engine
from src.lib.exceptions import (
    AppException,
    make_error_response,
)
from src.lib.redis import redis
from src.meetings.router import router as meetings_router
from src.notifications.router import router as notifications_router
from src.organizations.router import router as organizations_router
from src.tags.router import router as tags_router
from src.upload.router import router as upload_router

ENV = os.getenv("ENV", "dev")
IS_PROD = ENV == "prod"

CORS_ALLOW_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000",
    ).split(",")
    if o.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await redis.aclose()
    await engine.dispose()


app = FastAPI(
    title="Globe CRM API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "If-None-Match"],
    expose_headers=["ETag"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return make_error_response(exc)


app.include_router(auth_router)
app.include_router(contact_relationships_router)
app.include_router(contacts_router)
app.include_router(experiences_router)
app.include_router(graph_router)
app.include_router(imports_router)
app.include_router(meetings_router)
app.include_router(notifications_router)
app.include_router(geocoding_router)
app.include_router(export_router)
app.include_router(globe_router)
app.include_router(organizations_router)
app.include_router(tags_router)
app.include_router(upload_router)


@app.get("/health")
async def health() -> JSONResponse:
    db_ok = False
    redis_ok = False
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    try:
        await cast(Awaitable[bool], redis.ping())
        redis_ok = True
    except Exception:
        redis_ok = False

    overall_ok = db_ok and redis_ok
    body = {
        "status": "ok" if overall_ok else "degraded",
        "checks": {"db": db_ok, "redis": redis_ok},
    }
    return JSONResponse(content=body, status_code=200 if overall_ok else 503)
