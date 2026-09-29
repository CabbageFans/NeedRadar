from __future__ import annotations

import json
import logging
import logging.config
import re
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from typing import Any, NamedTuple
from urllib.parse import urlsplit

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)
project_id_context: ContextVar[str | None] = ContextVar("project_id", default=None)
job_id_context: ContextVar[str | None] = ContextVar("job_id", default=None)
stage_context: ContextVar[str] = ContextVar("stage", default="foundation")


class LogContextTokens(NamedTuple):
    request_id: Token[str | None]
    project_id: Token[str | None]
    job_id: Token[str | None]
    stage: Token[str]


def bind_log_context(
    *,
    request_id: str | None = None,
    project_id: str | None = None,
    job_id: str | None = None,
    stage: str = "foundation",
) -> LogContextTokens:
    return LogContextTokens(
        request_id_context.set(request_id),
        project_id_context.set(project_id),
        job_id_context.set(job_id),
        stage_context.set(stage),
    )


def reset_log_context(tokens: LogContextTokens) -> None:
    request_id_context.reset(tokens.request_id)
    project_id_context.reset(tokens.project_id)
    job_id_context.reset(tokens.job_id)
    stage_context.reset(tokens.stage)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        metadata = getattr(record, "metadata", {})
        if not isinstance(metadata, dict):
            metadata = {"value": str(metadata)}
        message = record.getMessage()
        if record.name == "uvicorn.access":
            message = "HTTP request completed"
            if isinstance(record.args, tuple) and len(record.args) >= 5:
                metadata = {
                    "method": str(record.args[1]),
                    "path": urlsplit(str(record.args[2])).path,
                    "status_code": int(str(record.args[4])),
                }
        message = re.sub(r"(postgresql\+psycopg://[^:/\s]+:)[^@\s]+(@)", r"\1***\2", message)
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "project_id": project_id_context.get(),
            "job_id": job_id_context.get(),
            "stage": stage_context.get(),
            "level": record.levelname,
            "message": message,
            "metadata": metadata,
            "request_id": request_id_context.get(),
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def uvicorn_log_config(level: str = "INFO") -> dict[str, Any]:
    normalized = level.upper()
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"needradar": {"()": "needradar.core.logging.JsonFormatter"}},
        "handlers": {
            "needradar": {
                "class": "logging.StreamHandler",
                "formatter": "needradar",
                "stream": "ext://sys.stderr",
            }
        },
        "loggers": {
            "uvicorn": {"handlers": ["needradar"], "level": normalized, "propagate": False},
            "uvicorn.error": {
                "handlers": ["needradar"],
                "level": normalized,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["needradar"],
                "level": normalized,
                "propagate": False,
            },
        },
        "root": {"handlers": ["needradar"], "level": normalized},
    }


def configure_logging(level: str) -> None:
    logging.config.dictConfig(uvicorn_log_config(level))
