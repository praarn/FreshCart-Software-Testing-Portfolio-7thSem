"""Consistent REST error shape: {status, error, message, field_errors: [{field, message}]}."""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        field_errors: list[dict] | None = None,
        headers: dict | None = None,
    ):
        self.status_code = status_code
        self.error = error
        self.message = message
        self.field_errors = field_errors or []
        self.headers = headers or {}


class BadRequestError(AppError):
    def __init__(self, message: str, field_errors: list[dict] | None = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, "BAD_REQUEST", message, field_errors)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required."):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "UNAUTHORIZED", message)


class ForbiddenError(AppError):
    def __init__(self, message: str = "You do not have access to this resource."):
        super().__init__(status.HTTP_403_FORBIDDEN, "FORBIDDEN", message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found."):
        super().__init__(status.HTTP_404_NOT_FOUND, "NOT_FOUND", message)


class ConflictError(AppError):
    def __init__(self, message: str, field_errors: list[dict] | None = None):
        super().__init__(status.HTTP_409_CONFLICT, "CONFLICT", message, field_errors)


class UnprocessableError(AppError):
    def __init__(self, message: str, field_errors: list[dict] | None = None):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR", message, field_errors)


class RateLimitedError(AppError):
    def __init__(self, retry_after: int):
        super().__init__(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "RATE_LIMITED",
            "Too many requests. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


def _body(status_code: int, error: str, message: str, field_errors: list[dict]) -> dict:
    return {"status": status_code, "error": error, "message": message, "field_errors": field_errors}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.status_code, exc.error, exc.message, exc.field_errors),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        field_errors = []
        for err in exc.errors():
            loc = [str(p) for p in err["loc"] if p not in ("body", "query", "path")]
            field_errors.append({"field": ".".join(loc) or "__root__", "message": err["msg"]})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_body(422, "VALIDATION_ERROR", "Validation failed.", field_errors),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        code_map = {400: "BAD_REQUEST", 401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 409: "CONFLICT", 429: "RATE_LIMITED"}
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.status_code, code_map.get(exc.status_code, "ERROR"), str(exc.detail), []),
            headers=getattr(exc, "headers", None) or {},
        )
