import datetime
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import src.registry  # noqa: F401  -- register every ORM model so all FKs resolve
from src.api.routers import v1
from src.config import Environment, settings
from src.exceptions import AppException
from src.schemas import ErrorResponse

SHOW_DOCS_IN = {Environment.LOCAL, Environment.STAGING}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Startup/shutdown hooks go here (warm caches, open clients, etc.).
    yield


def create_app() -> FastAPI:
    app_kwargs: dict = {
        "title": settings.PROJECT_NAME,
        "version": "0.1.0",
        "lifespan": lifespan,
    }
    if settings.ENVIRONMENT not in SHOW_DOCS_IN:
        app_kwargs["openapi_url"] = (
            None  # disables /docs and /redoc outside local/staging
        )

    app = FastAPI(**app_kwargs)

    app.add_middleware(
        cast(Any, CORSMiddleware),
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppException)
    async def _handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error_code=exc.error_code, detail=exc.detail
            ).model_dump(),
        )

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT.value,
            "app_name": settings.PROJECT_NAME,
            "version": app.version,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        }

    app.include_router(v1)

    return app


app = create_app()
