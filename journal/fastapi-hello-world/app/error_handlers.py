from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog

from app.exceptions import AppError

logger = structlog.get_logger("errors")


STATUS_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
}


def error_content(
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"error": error}


def code_for_status(status_code: int) -> str:
    if status_code in STATUS_ERROR_CODES:
        return STATUS_ERROR_CODES[status_code]
    return f"HTTP_{status_code}"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(
        _request: Request,
        exc: AppError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_content(exc.code, exc.message),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_content(code_for_status(exc.status_code), message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_content(
                "VALIDATION_ERROR",
                "Invalid request",
                jsonable_encoder(exc.errors()),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            method=request.method,
            path=request.url.path,
            exc_info=exc,
        )
        response = JSONResponse(
            status_code=500,
            content=error_content("INTERNAL_ERROR", "Something went wrong"),
        )
        correlation_id = structlog.contextvars.get_contextvars().get("correlation_id")
        if correlation_id:
            response.headers["X-Request-ID"] = str(correlation_id)
        return response
