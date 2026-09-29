from __future__ import annotations

import hashlib

import pytest
from needradar.testing.database_safety import (
    LocalGuardCredential,
    PersistentGuard,
    validate_test_database_target,
)
from needradar.testing.database_safety import TestDatabaseSafetyError as SafetyError

pytestmark = pytest.mark.unit

SAFE_URL = "postgresql+psycopg://needradar_test:unit-password@127.0.0.1:55432/needradar_test"
TOKEN = "local-random-token"
TOKEN_HASH = hashlib.sha256(TOKEN.encode()).hexdigest()


def local_guard(**overrides: object) -> LocalGuardCredential:
    values: dict[str, object] = {
        "schema_version": 1,
        "database_name": "needradar_test",
        "host": "127.0.0.1",
        "port": 55432,
        "guard_id": "guard-123",
        "guard_token": TOKEN,
        "created_at": "2026-09-28T00:00:00Z",
    }
    values.update(overrides)
    return LocalGuardCredential(**values)  # type: ignore[arg-type]


def persistent_guard(**overrides: object) -> PersistentGuard:
    values: dict[str, object] = {
        "current_database": "needradar_test",
        "guard_version": 1,
        "environment": "TEST",
        "database_name": "needradar_test",
        "guard_id": "guard-123",
        "guard_token_hash": TOKEN_HASH,
    }
    values.update(overrides)
    return PersistentGuard(**values)  # type: ignore[arg-type]


def validate(
    test_url: str | None,
    *,
    development_url: str | None = None,
    local: LocalGuardCredential | None = None,
    persistent: PersistentGuard | None = None,
) -> None:
    validate_test_database_target(
        test_database_url=test_url,
        development_database_url=development_url,
        credential_loader=lambda: local if local is not None else local_guard(),
        guard_probe=lambda _: persistent if persistent is not None else persistent_guard(),
    )


def test_db_safe_001_missing_test_database_url_rejects() -> None:
    with pytest.raises(SafetyError, match="TEST_DATABASE_URL is required"):
        validate(None)


def test_db_safe_002_same_as_development_database_rejects() -> None:
    with pytest.raises(SafetyError, match="must not target DATABASE_URL"):
        validate(SAFE_URL, development_url=SAFE_URL)


def test_db_safe_003_unsafe_database_name_rejects() -> None:
    unsafe = "postgresql+psycopg://user:secret@127.0.0.1:55432/needradar"
    with pytest.raises(SafetyError, match="needradar_test"):
        validate(unsafe)


def test_db_safe_004_missing_persistent_guard_rejects() -> None:
    with pytest.raises(SafetyError, match="Persistent"):
        validate_test_database_target(
            test_database_url=SAFE_URL,
            development_database_url=None,
            credential_loader=local_guard,
            guard_probe=lambda _: None,
        )


def test_db_safe_005_missing_local_guard_rejects() -> None:
    def missing() -> LocalGuardCredential:
        raise SafetyError("Local test database guard credential is missing")

    with pytest.raises(SafetyError, match="Local"):
        validate_test_database_target(
            test_database_url=SAFE_URL,
            development_database_url=None,
            credential_loader=missing,
            guard_probe=lambda _: persistent_guard(),
        )


@pytest.mark.parametrize(
    "persistent",
    [
        persistent_guard(guard_id="other"),
        persistent_guard(guard_token_hash="0" * 64),
        persistent_guard(database_name="needradar_test_other"),
        persistent_guard(current_database="needradar_test_other"),
        persistent_guard(environment="DEVELOPMENT"),
    ],
)
def test_db_safe_006_guard_mismatch_rejects(persistent: PersistentGuard) -> None:
    with pytest.raises(SafetyError, match="Persistent"):
        validate(SAFE_URL, persistent=persistent)


def test_db_safe_007_valid_three_layer_guard_allows() -> None:
    target = validate_test_database_target(
        test_database_url=SAFE_URL,
        development_database_url=None,
        credential_loader=local_guard,
        guard_probe=lambda _: persistent_guard(),
    )
    assert target.database == "needradar_test"
    assert target.guard_id == "guard-123"


@pytest.mark.parametrize("database", ["postgres", "template0", "template1"])
def test_db_safe_008_protected_postgres_databases_reject(database: str) -> None:
    unsafe = f"postgresql+psycopg://user:secret@127.0.0.1:55432/{database}"
    with pytest.raises(SafetyError, match="needradar_test"):
        validate(unsafe)


def test_db_safe_009_forged_libpq_session_option_rejects() -> None:
    forged = SAFE_URL + "?options=-cneedradar.environment%3DTEST"
    with pytest.raises(SafetyError, match="session options"):
        validate(forged)


def test_db_safe_010_failure_never_exposes_password() -> None:
    password = "do-not-leak-this-password"
    unsafe = f"postgresql+psycopg://needradar_test:{password}@127.0.0.1:55432/needradar_test"
    with pytest.raises(SafetyError) as caught:
        validate_test_database_target(
            test_database_url=unsafe,
            development_database_url=None,
            credential_loader=local_guard,
            guard_probe=lambda _: None,
        )
    assert password not in str(caught.value)


@pytest.mark.parametrize(
    "unsafe",
    [
        "postgresql+psycopg://user:secret@127.0.0.1:5432/needradar_test",
        "postgresql+psycopg://user:secret@database.example:55432/needradar_test",
        "postgresql+psycopg://user:secret@127.0.0.1:55432/contest_production",
        "sqlite:///needradar_test.db",
    ],
)
def test_validator_fails_closed_for_unapproved_targets(unsafe: str) -> None:
    with pytest.raises(SafetyError):
        validate(unsafe)
