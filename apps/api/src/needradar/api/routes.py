from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from needradar import __version__
from needradar.api.errors import ProblemDetails, problem_response
from needradar.db.readiness import ReadinessResult

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: Literal["needradar-api"]
    version: str


class ReadyResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: Literal["ready"]
    database: Literal["ok"]
    schema_state: Literal["head"] = Field(alias="schema")
    revision: str


@router.get("/health", response_model=HealthResponse, tags=["foundation"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="needradar-api", version=__version__)


@router.get(
    "/ready",
    response_model=ReadyResponse,
    responses={
        503: {
            "model": ProblemDetails,
            "description": "Foundation dependencies are not ready",
        }
    },
    tags=["foundation"],
)
async def ready(request: Request) -> ReadyResponse | JSONResponse:
    result: ReadinessResult = await request.app.state.readiness.check()
    if result.ready:
        return ReadyResponse(
            status="ready",
            database="ok",
            schema_state="head",
            revision=result.revision or "",
        )

    code = "SERVICE_NOT_READY" if result.database == "unavailable" else "SCHEMA_NOT_READY"
    return problem_response(
        request,
        status=503,
        code=code,
        title="Service not ready",
        detail=result.detail,
        extra={"database": result.database, "schema": result.schema},
    )
