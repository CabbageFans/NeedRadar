from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict


class ProblemDetails(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    title: str
    status: int
    detail: str
    code: str
    request_id: str
    field_errors: list[dict[str, Any]] | None = None


def problem_response(
    request: Request,
    *,
    status: int,
    code: str,
    title: str,
    detail: str,
    extra: dict[str, Any] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "type": f"urn:needradar:problem:{code.lower()}",
        "title": title,
        "status": status,
        "detail": detail,
        "code": code,
        "request_id": request.state.request_id,
    }
    if extra:
        payload.update(extra)
    return JSONResponse(
        status_code=status,
        content=payload,
        media_type="application/problem+json",
    )


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {
                "location": [str(part) for part in error["loc"]],
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        return problem_response(
            request,
            status=422,
            code="VALIDATION_ERROR",
            title="Request validation failed",
            detail="One or more request fields are invalid.",
            extra={"field_errors": errors},
        )
