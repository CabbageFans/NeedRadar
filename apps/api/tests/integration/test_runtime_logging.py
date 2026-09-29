from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from needradar.testing.database_safety import SafeTestDatabase

pytestmark = pytest.mark.integration

REQUIRED_FIELDS = {"timestamp", "project_id", "job_id", "stage", "level", "message", "metadata"}


def available_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def test_real_uvicorn_startup_and_access_logs_are_structured(
    safe_test_database: SafeTestDatabase, tmp_path: Path
) -> None:
    port = available_port()
    log_path = tmp_path / "uvicorn.jsonl"
    environment = os.environ.copy()
    environment["TEST_DATABASE_URL"] = safe_test_database.url
    environment["PYTHONPATH"] = "apps/api/src"
    with log_path.open("w+", encoding="utf-8") as output:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "needradar.testing.database_safety",
                "serve-e2e",
                "--port",
                str(port),
            ],
            cwd=Path(__file__).parents[4],
            env=environment,
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            response: httpx.Response | None = None
            for _ in range(80):
                try:
                    response = httpx.get(
                        f"http://127.0.0.1:{port}/health?token=runtime-secret", timeout=0.5
                    )
                    break
                except httpx.TransportError:
                    time.sleep(0.1)
            assert response is not None and response.status_code == 200
        finally:
            process.terminate()
            process.wait(timeout=10)
        output.flush()
    raw = log_path.read_text(encoding="utf-8")
    records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    assert records
    assert all(REQUIRED_FIELDS <= set(record) for record in records)
    assert any("Started server process" in record["message"] for record in records)
    access = [record for record in records if record["message"] == "HTTP request completed"]
    assert access
    assert access[-1]["metadata"]["path"] == "/health"
    assert access[-1]["metadata"]["status_code"] == 200
    assert "runtime-secret" not in raw
