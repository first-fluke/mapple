from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ApiResponse[T](BaseModel):
    data: T
    meta: dict[str, Any] | None = None
    errors: list[ErrorDetail] | None = None


class AppException(Exception):
    def __init__(
        self,
        *,
        status_code: int = 400,
        code: str,
        message: str,
        details: Any = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(status_code=404, code="NOT_FOUND", message=message, **kwargs)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists", **kwargs: Any) -> None:
        super().__init__(status_code=409, code="CONFLICT", message=message, **kwargs)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", **kwargs: Any) -> None:
        super().__init__(status_code=401, code="UNAUTHORIZED", message=message, **kwargs)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", **kwargs: Any) -> None:
        super().__init__(status_code=403, code="FORBIDDEN", message=message, **kwargs)


def make_error_response(exc: AppException) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorDetail(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(mode="json"),
    )
