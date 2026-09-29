from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from needradar.testing.database_safety import (
    SafeTestDatabase,
    assert_safe_test_database,
    safe_alembic_config,
)
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

REPOSITORY_ROOT = Path(__file__).parents[3]
ALEMBIC_CONFIG_PATH = REPOSITORY_ROOT / "apps/api/alembic.ini"


def alembic_config(target: SafeTestDatabase) -> Config:
    return safe_alembic_config(target)


@pytest.fixture
def safe_test_database() -> SafeTestDatabase:
    return assert_safe_test_database()


@pytest.fixture
def test_database_url(safe_test_database: SafeTestDatabase) -> str:
    return safe_test_database.url


@pytest.fixture
def migrated_database(safe_test_database: SafeTestDatabase) -> Iterator[SafeTestDatabase]:
    config = alembic_config(safe_test_database)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    yield safe_test_database
    command.downgrade(config, "base")
    command.upgrade(config, "head")


@pytest.fixture
async def database_engine(migrated_database: SafeTestDatabase) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(migrated_database.url, pool_pre_ping=True)
    yield engine
    await engine.dispose()
