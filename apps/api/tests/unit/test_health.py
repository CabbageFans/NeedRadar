from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from needradar.api.app import create_app
from needradar.core.config import Settings

pytestmark = pytest.mark.unit


def test_health_does_not_connect_to_database() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://unused:unused@127.0.0.1:1/unused",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "needradar-api",
        "version": "0.1.0",
    }
    assert response.headers["X-Request-ID"]


def test_cors_allows_declared_local_origin_only() -> None:
    settings = Settings(_env_file=None)
    with TestClient(create_app(settings)) as client:
        allowed = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        denied = client.options(
            "/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-origin" not in denied.headers
