from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import check_connection, init_db
from .logging import configure_logging
from .middleware.auth import JWTMiddleware
from .middleware.ratelimit import RateLimitMiddleware
from .monitoring import setup_monitoring
from .routes import ai, auth, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    s = get_settings()
    configure_logging()
    app = FastAPI(title="Onoma AI Genesis", version="1.0.0", lifespan=lifespan)
    app.add_middleware(JWTMiddleware)
    app.add_middleware(RateLimitMiddleware, per_minute=s.rate_limit_per_minute)
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_origin_list, allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])
    setup_monitoring(app, s.sentry_dsn)
    app.include_router(auth.router)
    app.include_router(ai.router)
    app.include_router(projects.router)

    @app.get("/api/health")
    def health():
        return {"status": "operational", "version": "1.0.0"}

    @app.get("/api/health/db")
    def health_db():
        if not check_connection():
            raise HTTPException(503, "database unavailable")
        return {"database": "ok"}

    return app


app = create_app()
