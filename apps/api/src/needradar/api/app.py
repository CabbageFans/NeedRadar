from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from needradar import __version__
from needradar.api.errors import install_error_handlers
from needradar.api.middleware import RequestContextMiddleware
from needradar.api.routes import router
from needradar.core.config import Settings, load_settings
from needradar.core.logging import configure_logging
from needradar.db.engine import DatabaseRuntime
from needradar.db.readiness import ReadinessService


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = DatabaseRuntime.create(resolved_settings.database_url)
        app.state.database = database
        app.state.readiness = ReadinessService(
            engine=database.engine,
            alembic_config_path=resolved_settings.alembic_config_path,
        )
        try:
            yield
        finally:
            await database.dispose()

    app = FastAPI(
        title="NeedRadar Foundation API",
        version=__version__,
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in resolved_settings.cors_origins],
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Content-Type", "X-Request-ID"],
    )
    install_error_handlers(app)
    app.include_router(router)
    return app
