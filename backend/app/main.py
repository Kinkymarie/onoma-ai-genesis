"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config.security import get_security_settings
from .config.settings import get_settings
from .dependencies import container
from .jobs import cleanup_tasks, notification_tasks, runner
from .middleware.auth import JWTMiddleware
from .middleware.cors import configure_cors
from .middleware.errors import register_error_handlers
from .middleware.logging import RequestLoggingMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .routes import api_router
from .utils.constants import API_PREFIX, APP_NAME, APP_VERSION
from .utils.logger import configure_logging, get_logger

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    if settings.is_production and "jwt_secret_key" not in get_security_settings().model_fields_set:
        raise RuntimeError("JWT_SECRET_KEY must be set in production")
    if settings.sentry_dsn:
        try:
            import sentry_sdk
            sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)
        except ImportError:
            log.warning("sentry-sdk not installed; error reporting disabled")
    runner.register("purge_tokens", cleanup_tasks.purge_expired_tokens, 3600)
    runner.register("purge_audit", lambda: cleanup_tasks.purge_old_audit_logs(container.repos), 86400)
    runner.register("overdue_tasks", lambda: notification_tasks.notify_overdue_tasks(container.repos), 3600)
    runner.start()
    log.info("startup complete")
    yield
    runner.stop()
    log.info("shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan,
                  docs_url=None if settings.is_production else "/docs",
                  redoc_url=None if settings.is_production else "/redoc")
    register_error_handlers(app)
    app.add_middleware(JWTMiddleware)
    app.add_middleware(RateLimitMiddleware, limit_per_minute=settings.rate_limit_per_minute)
    app.add_middleware(RequestLoggingMiddleware)
    configure_cors(app)
    app.include_router(api_router, prefix=API_PREFIX)

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok", "version": APP_VERSION}

    @app.get("/health/ready", tags=["health"])
    def ready():
        return {"status": "ready", "backend": "memory", "users": container.repos.users.count()}

    return app


app = create_app()
