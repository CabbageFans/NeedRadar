from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from needradar.api.app import create_app
from needradar.core.config import Settings, load_settings
from pydantic import ValidationError

pytestmark = pytest.mark.unit


def test_defaults_are_local_and_psycopg() -> None:
    settings = Settings(_env_file=None)
    assert settings.api_host == "127.0.0.1"
    assert settings.database_url.startswith("postgresql+psycopg://")
    assert {str(origin).rstrip("/") for origin in settings.cors_origins} == {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }
    repository_root = Path(__file__).parents[4]
    web_package = json.loads((repository_root / "apps/web/package.json").read_text())
    assert "${WEB_PORT:-3000}" in web_package["scripts"]["dev"]


@pytest.mark.parametrize(
    ("field", "value"),
    [("api_host", "0.0.0.0"), ("cors_origins", "*"), ("database_url", "sqlite:///tmp.db")],
)
def test_unsafe_boundaries_are_rejected(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{field: value})


@pytest.mark.parametrize(
    "origin",
    [
        "http://example.com",
        "https://example.com",
        "https://localhost:3000",
        "http://localhost:3000/path",
        "http://localhost:3000?token=secret",
        "http://localhost:3000#fragment",
        "http://user:password@localhost:3000",
        "not-an-origin",
    ],
)
def test_remote_or_non_origin_cors_values_are_rejected(origin: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins=[origin])


@pytest.mark.parametrize(
    "origin",
    ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:43117"],
)
def test_local_http_origins_are_allowed(origin: str) -> None:
    settings = Settings(_env_file=None, cors_origins=[origin])
    assert str(settings.cors_origins[0]).rstrip("/") == origin


def test_env_example_is_an_executable_clean_setup_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository_root = Path(__file__).parents[4]
    template = (repository_root / ".env.example").read_text(encoding="utf-8")
    env_text = template.replace(
        "needradar:change-me@127.0.0.1:5432",
        "needradar:needradar_local@127.0.0.1:5432",
    ).replace(
        "needradar_test:change-me@127.0.0.1:55432",
        "needradar_test:needradar_test_local@127.0.0.1:55432",
    )
    env_file = tmp_path / ".env"
    env_file.write_text(env_text, encoding="utf-8")
    monkeypatch.setenv("NEEDRADAR_ENV_FILE", str(env_file))

    settings = load_settings()
    origins = {str(origin).rstrip("/") for origin in settings.cors_origins}
    assert origins == {"http://localhost:3000", "http://127.0.0.1:3000"}
    assert settings.database_url.endswith("@127.0.0.1:5432/needradar")
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000

    app = create_app(settings)
    with TestClient(app) as client:
        health = client.get("/health")
        preflight = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
    client_visible = json.dumps(
        {"health": health.json(), "openapi": app.openapi()}, ensure_ascii=False
    )
    assert health.status_code == 200
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "needradar_local" not in client_visible
    assert "needradar_test_local" not in client_visible
    assert "change-me" not in client_visible
