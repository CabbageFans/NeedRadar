from __future__ import annotations

import json
import logging

import pytest
from needradar.core.logging import JsonFormatter, bind_log_context, reset_log_context

pytestmark = pytest.mark.unit


def test_structured_log_has_required_nullable_context() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "API alive", (), None)
    record.metadata = {"probe": "health"}
    tokens = bind_log_context(stage="health")
    try:
        payload = json.loads(formatter.format(record))
    finally:
        reset_log_context(tokens)
    assert set(payload) == {
        "timestamp",
        "project_id",
        "job_id",
        "stage",
        "level",
        "message",
        "metadata",
        "request_id",
    }
    assert payload["project_id"] is None
    assert payload["job_id"] is None
    assert payload["stage"] == "health"
    assert payload["metadata"] == {"probe": "health"}


def test_uvicorn_access_log_is_structured_and_drops_query_secrets() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        __file__,
        1,
        '%s - "%s %s HTTP/%s" %d',
        ("127.0.0.1:12345", "GET", "/health?token=do-not-log", "1.1", 200),
        None,
    )
    payload = json.loads(formatter.format(record))
    assert payload["message"] == "HTTP request completed"
    assert payload["metadata"] == {
        "method": "GET",
        "path": "/health",
        "status_code": 200,
    }
    assert "do-not-log" not in json.dumps(payload)
