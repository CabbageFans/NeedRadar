from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from conftest import ALEMBIC_CONFIG_PATH, alembic_config
from fastapi.testclient import TestClient
from needradar.api.app import create_app
from needradar.core.config import Settings
from needradar.testing.database_safety import SafeTestDatabase
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.integration


def settings_for(database_url: str) -> Settings:
    return Settings(
        _env_file=None,
        database_url=database_url,
        alembic_config_path=Path(ALEMBIC_CONFIG_PATH),
    )


@pytest.mark.quality_binding("REQ-ARCH-002")
@pytest.mark.quality_binding("REQ-FOUNDATION-001", "AC-FOUNDATION-001")
def test_ready_when_database_is_at_head(migrated_database: SafeTestDatabase) -> None:
    app = create_app(settings_for(migrated_database.url))
    with TestClient(app) as client:
        response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["schema"] == "head"
    assert response.json()["revision"] == "20260928_0001"
    assert app.state.database.engine.sync_engine.pool.checkedout() == 0


@pytest.mark.quality_binding("REQ-FOUNDATION-001", "AC-FOUNDATION-001")
def test_health_stays_up_when_database_is_down() -> None:
    unavailable = "postgresql+psycopg://unused:unused@127.0.0.1:1/unused?connect_timeout=1"
    with TestClient(create_app(settings_for(unavailable))) as client:
        health = client.get("/health")
        readiness = client.get("/ready")
    assert health.status_code == 200
    assert readiness.status_code == 503
    assert readiness.json()["database"] == "unavailable"
    assert readiness.json()["code"] == "SERVICE_NOT_READY"


def test_ready_rejects_schema_behind(safe_test_database: SafeTestDatabase) -> None:
    config = alembic_config(safe_test_database)
    command.downgrade(config, "base")
    try:
        with TestClient(create_app(settings_for(safe_test_database.url))) as client:
            response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["schema"] == "behind"
    finally:
        command.upgrade(config, "head")


@pytest.mark.asyncio
async def test_ready_rejects_unknown_revision(migrated_database: SafeTestDatabase) -> None:
    engine = create_async_engine(migrated_database.url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text("UPDATE alembic_version SET version_num = 'unknown_revision'")
            )
        with TestClient(create_app(settings_for(migrated_database.url))) as client:
            response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["schema"] == "unknown"
    finally:
        async with engine.begin() as connection:
            await connection.execute(
                text("UPDATE alembic_version SET version_num = '20260928_0001'")
            )
        await engine.dispose()


@pytest.mark.asyncio
async def test_ready_rejects_divergent_revisions(migrated_database: SafeTestDatabase) -> None:
    engine = create_async_engine(migrated_database.url)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text("INSERT INTO alembic_version (version_num) VALUES ('divergent_revision')")
            )
        with TestClient(create_app(settings_for(migrated_database.url))) as client:
            response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["schema"] == "divergent"
    finally:
        async with engine.begin() as connection:
            await connection.execute(
                text("DELETE FROM alembic_version WHERE version_num = 'divergent_revision'")
            )
        await engine.dispose()


@pytest.mark.asyncio
async def test_ready_rejects_missing_revision_metadata(
    migrated_database: SafeTestDatabase,
) -> None:
    engine = create_async_engine(migrated_database.url)
    try:
        async with engine.begin() as connection:
            await connection.execute(text("DROP TABLE alembic_version"))
        with TestClient(create_app(settings_for(migrated_database.url))) as client:
            response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["schema"] == "missing"
    finally:
        await engine.dispose()
