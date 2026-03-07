from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.shared.errors.app_error import AppError
from src.shared.http.response import error_response


def attach_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(code=exc.code, message=exc.message, retryable=exc.retryable),
        )

    @app.exception_handler(Exception)
    async def handle_generic_error(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=error_response(code="INTERNAL_ERROR", message="Unexpected error", retryable=True),
        )
