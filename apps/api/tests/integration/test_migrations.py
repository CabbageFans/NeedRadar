from __future__ import annotations

import pytest
from alembic import command
from alembic.runtime.migration import MigrationContext
from conftest import alembic_config
from needradar.testing.database_safety import SafeTestDatabase
from sqlalchemy import create_engine, inspect

pytestmark = [pytest.mark.integration, pytest.mark.migration]

EXPECTED_REVISION = "20260928_0001"


def schema_state(database_url: str) -> tuple[str | None, set[str]]:
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            revision = MigrationContext.configure(connection).get_current_revision()
            tables = set(inspect(connection).get_table_names())
            return revision, tables
    finally:
        engine.dispose()


@pytest.mark.quality_binding("REQ-ARCH-002")
@pytest.mark.quality_binding("REQ-GOVERNANCE-011", "AC-GOVERNANCE-011")
def test_empty_baseline_upgrade_downgrade_upgrade(
    safe_test_database: SafeTestDatabase,
) -> None:
    config = alembic_config(safe_test_database)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    revision, tables = schema_state(safe_test_database.url)
    assert revision == EXPECTED_REVISION
    assert tables == {"alembic_version"}

    command.downgrade(config, "base")
    revision, tables = schema_state(safe_test_database.url)
    assert revision is None
    assert tables <= {"alembic_version"}

    command.upgrade(config, "head")
    revision, tables = schema_state(safe_test_database.url)
    assert revision == EXPECTED_REVISION
    assert tables == {"alembic_version"}
