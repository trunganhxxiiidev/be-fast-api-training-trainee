import uvicorn
from fastapi import FastAPI

from app.config import Settings, get_settings
from app.error_handlers import register_exception_handlers
from app.logging_setup import setup_logging
from app.middleware import RequestLoggerMiddleware
from app.routes import echo, health, posts, users, version


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    setup_logging(app_settings.log_level)

    app = FastAPI(
        title="Hello API",
        version=app_settings.app_version,
        description="A small structured FastAPI service for Week 2 practice.",
    )
    app.state.settings = app_settings

    app.add_middleware(RequestLoggerMiddleware)
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(echo.router)
    app.include_router(version.router)
    app.include_router(users.router)
    app.include_router(posts.router)

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=get_settings().port, reload=True)
