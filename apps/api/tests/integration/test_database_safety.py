from __future__ import annotations

import pytest
from needradar.testing.database_safety import (
    SafeTestDatabase,
    assert_safe_test_database,
    validate_test_database_target,
)
from needradar.testing.database_safety import (
    TestDatabaseSafetyError as SafetyError,
)
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

pytestmark = pytest.mark.integration


def test_persistent_and_local_test_database_guards_are_verified(
    safe_test_database: SafeTestDatabase,
) -> None:
    independently_verified = assert_safe_test_database()
    assert independently_verified == safe_test_database
    engine = create_engine(safe_test_database.url)
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT environment, database_name, guard_id "
                    "FROM needradar_test_guard.identity WHERE singleton = TRUE"
                )
            ).one()
    finally:
        engine.dispose()
    assert row == ("TEST", safe_test_database.database, safe_test_database.guard_id)


def test_forged_libpq_session_option_cannot_authorize_database() -> None:
    forged = (
        "postgresql+psycopg://needradar_test:forged@127.0.0.1:55432/needradar_test"
        "?options=-cneedradar.environment%3DTEST"
    )
    with pytest.raises(SafetyError, match="session options"):
        validate_test_database_target(
            test_database_url=forged,
            development_database_url=None,
        )


def test_db_safe_011_rejected_protected_database_is_not_modified(
    safe_test_database: SafeTestDatabase,
) -> None:
    unsafe_url = (
        make_url(safe_test_database.url)
        .set(database="postgres")
        .render_as_string(hide_password=False)
    )
    engine = create_engine(unsafe_url)
    try:
        with engine.connect() as connection:
            before_tables = set(inspect(connection).get_table_names(schema="public"))
            before_databases = tuple(
                connection.execute(
                    text("SELECT datname FROM pg_database ORDER BY datname")
                ).scalars()
            )

        with pytest.raises(SafetyError):
            validate_test_database_target(
                test_database_url=unsafe_url,
                development_database_url=None,
            )

        with engine.connect() as connection:
            after_tables = set(inspect(connection).get_table_names(schema="public"))
            after_databases = tuple(
                connection.execute(
                    text("SELECT datname FROM pg_database ORDER BY datname")
                ).scalars()
            )
    finally:
        engine.dispose()

    assert after_tables == before_tables
    assert after_databases == before_databases
