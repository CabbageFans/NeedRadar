from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, cast
from uuid import uuid4

import uvicorn
from alembic import command
from alembic.config import Config
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.pool import NullPool

from needradar.core.logging import uvicorn_log_config

TEST_DATABASE_NAME_RE = re.compile(r"^needradar_test(?:_[a-z0-9_]+)?$")
ALLOWED_TEST_HOSTS = frozenset({"127.0.0.1", "localhost"})
TEST_POSTGRES_PORT = 55432
PROTECTED_DATABASE_NAMES = frozenset({"needradar", "postgres", "template0", "template1"})
GUARD_SCHEMA_VERSION = 1
GUARD_ENVIRONMENT = "TEST"
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
ALEMBIC_CONFIG_PATH = REPOSITORY_ROOT / "apps/api/alembic.ini"
LOCAL_GUARD_PATH = REPOSITORY_ROOT / ".needradar/test-db-guard.json"


class TestDatabaseSafetyError(RuntimeError):
    """Raised before a test database operation when isolation cannot be proven."""


@dataclass(frozen=True, slots=True)
class PersistentGuard:
    current_database: str
    guard_version: int
    environment: str
    database_name: str
    guard_id: str
    guard_token_hash: str


@dataclass(frozen=True, slots=True)
class LocalGuardCredential:
    schema_version: int
    database_name: str
    host: str
    port: int
    guard_id: str
    guard_token: str
    created_at: str


class GuardProbe(Protocol):
    def __call__(self, database_url: str) -> PersistentGuard | None: ...


class CredentialLoader(Protocol):
    def __call__(self) -> LocalGuardCredential: ...


@dataclass(frozen=True, slots=True)
class SafeTestDatabase:
    url: str
    host: str
    port: int
    database: str
    guard_id: str

    @property
    def safe_identity(self) -> str:
        return f"host={self.host} port={self.port} database={self.database}"


class TestDatabaseEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    test_database_url: str | None = None
    test_database_admin_url: str | None = None
    database_url: str | None = None


def _parse_database_url(value: str, *, variable: str) -> URL:
    try:
        url = make_url(value)
    except Exception:
        raise TestDatabaseSafetyError(f"{variable} is not a valid database URL") from None
    if url.drivername != "postgresql+psycopg":
        raise TestDatabaseSafetyError(f"{variable} must use postgresql+psycopg")
    if "options" in url.query:
        raise TestDatabaseSafetyError(f"{variable} must not contain libpq session options")
    return url


def _identity(url: URL) -> tuple[str, int, str]:
    host = (url.host or "").lower()
    normalized_host = "127.0.0.1" if host == "localhost" else host
    return normalized_host, url.port or 5432, url.database or ""


def _safe_target_identity(
    *, test_database_url: str | None, development_database_url: str | None
) -> tuple[URL, str, int, str, str]:
    if not test_database_url:
        raise TestDatabaseSafetyError(
            "TEST_DATABASE_URL is required for destructive test database operations"
        )
    test_url = _parse_database_url(test_database_url, variable="TEST_DATABASE_URL")
    host, port, database = _identity(test_url)
    display_host = test_url.host or "<missing>"
    safe_identity = f"host={display_host} port={port} database={database or '<missing>'}"
    if display_host.lower() not in ALLOWED_TEST_HOSTS or port != TEST_POSTGRES_PORT:
        raise TestDatabaseSafetyError(
            f"TEST_DATABASE_URL must target the dedicated local test PostgreSQL; {safe_identity}"
        )
    if database in PROTECTED_DATABASE_NAMES or not TEST_DATABASE_NAME_RE.fullmatch(database):
        raise TestDatabaseSafetyError(
            "TEST_DATABASE_URL database must be needradar_test or needradar_test_*; "
            f"{safe_identity}"
        )
    if development_database_url:
        development_url = _parse_database_url(development_database_url, variable="DATABASE_URL")
        if _identity(development_url) == (host, port, database):
            raise TestDatabaseSafetyError(
                f"TEST_DATABASE_URL must not target DATABASE_URL; {safe_identity}"
            )
    return test_url, host, port, database, display_host


def _read_persistent_guard(database_url: str) -> PersistentGuard | None:
    engine = create_engine(database_url, poolclass=NullPool)
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("SET TRANSACTION READ ONLY"))
                row = connection.execute(
                    text(
                        "SELECT current_database(), guard_version, environment, database_name, "
                        "guard_id, guard_token_hash FROM needradar_test_guard.identity "
                        "WHERE singleton = TRUE"
                    )
                ).one_or_none()
                if row is None:
                    return None
                return PersistentGuard(
                    current_database=cast(str, row[0]),
                    guard_version=cast(int, row[1]),
                    environment=cast(str, row[2]),
                    database_name=cast(str, row[3]),
                    guard_id=cast(str, row[4]),
                    guard_token_hash=cast(str, row[5]),
                )
    except Exception:
        return None
    finally:
        engine.dispose()


def _load_local_guard() -> LocalGuardCredential:
    try:
        resolved = LOCAL_GUARD_PATH.resolve(strict=True)
        if resolved != LOCAL_GUARD_PATH or LOCAL_GUARD_PATH.is_symlink():
            raise TestDatabaseSafetyError("Local test database guard must not be a symlink")
        raw = json.loads(LOCAL_GUARD_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError
        return LocalGuardCredential(
            schema_version=int(raw["schema_version"]),
            database_name=str(raw["database_name"]),
            host=str(raw["host"]),
            port=int(raw["port"]),
            guard_id=str(raw["guard_id"]),
            guard_token=str(raw["guard_token"]),
            created_at=str(raw["created_at"]),
        )
    except TestDatabaseSafetyError:
        raise
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        raise TestDatabaseSafetyError(
            "Local test database guard credential is missing or invalid"
        ) from None


def validate_test_database_target(
    *,
    test_database_url: str | None,
    development_database_url: str | None,
    guard_probe: GuardProbe = _read_persistent_guard,
    credential_loader: CredentialLoader = _load_local_guard,
) -> SafeTestDatabase:
    """Return a target only after URL, persistent guard, and local credential agree."""
    _, host, port, database, display_host = _safe_target_identity(
        test_database_url=test_database_url,
        development_database_url=development_database_url,
    )
    assert test_database_url is not None
    try:
        credential = credential_loader()
    except TestDatabaseSafetyError:
        raise
    except Exception:
        raise TestDatabaseSafetyError(
            "Local test database guard credential is missing or invalid"
        ) from None
    if (
        credential.schema_version != GUARD_SCHEMA_VERSION
        or credential.database_name != database
        or credential.host != host
        or credential.port != port
        or not credential.guard_id
        or not credential.guard_token
    ):
        raise TestDatabaseSafetyError("Local test database guard does not match the target")
    try:
        guard = guard_probe(test_database_url)
    except Exception:
        guard = None
    expected_hash = hashlib.sha256(credential.guard_token.encode("utf-8")).hexdigest()
    if (
        guard is None
        or guard.guard_version != GUARD_SCHEMA_VERSION
        or guard.environment != GUARD_ENVIRONMENT
        or guard.current_database != database
        or guard.database_name != database
        or guard.guard_id != credential.guard_id
        or not hmac.compare_digest(guard.guard_token_hash, expected_hash)
    ):
        raise TestDatabaseSafetyError("Persistent test database guard is missing or invalid")
    return SafeTestDatabase(test_database_url, display_host, port, database, credential.guard_id)


def assert_safe_test_database(*, env_file: str | Path | None = ".env") -> SafeTestDatabase:
    settings = TestDatabaseEnvironment(_env_file=env_file)
    return validate_test_database_target(
        test_database_url=settings.test_database_url,
        development_database_url=settings.database_url,
    )


def _write_local_guard(credential: LocalGuardCredential) -> None:
    if LOCAL_GUARD_PATH.exists() or LOCAL_GUARD_PATH.is_symlink():
        raise TestDatabaseSafetyError("Refusing to overwrite an existing local test database guard")
    LOCAL_GUARD_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = LOCAL_GUARD_PATH.with_suffix(f".{uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(asdict(credential), indent=2) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(LOCAL_GUARD_PATH)
    finally:
        if temporary.exists():
            temporary.unlink()


def _database_exists(admin_url: str, database: str) -> bool:
    engine = create_engine(admin_url, poolclass=NullPool)
    try:
        with engine.connect() as connection:
            return (
                connection.scalar(
                    text("SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = :database)"),
                    {"database": database},
                )
                is True
            )
    finally:
        engine.dispose()


def _create_database(admin_url: str, database: str) -> None:
    engine = create_engine(admin_url, poolclass=NullPool, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql(f'CREATE DATABASE "{database}"')
    finally:
        engine.dispose()


def _install_persistent_guard(database_url: str, credential: LocalGuardCredential) -> None:
    token_hash = hashlib.sha256(credential.guard_token.encode("utf-8")).hexdigest()
    engine = create_engine(database_url, poolclass=NullPool)
    try:
        with engine.begin() as connection:
            actual_database = connection.scalar(text("SELECT current_database()"))
            if actual_database != credential.database_name:
                raise TestDatabaseSafetyError("Bootstrap connection resolved to the wrong database")
            connection.execute(text("CREATE SCHEMA needradar_test_guard"))
            connection.execute(
                text(
                    "CREATE TABLE needradar_test_guard.identity ("
                    "singleton boolean PRIMARY KEY DEFAULT TRUE CHECK (singleton), "
                    "guard_version integer NOT NULL, environment text NOT NULL, "
                    "database_name text NOT NULL, guard_id text NOT NULL, "
                    "guard_token_hash text NOT NULL, created_at timestamptz NOT NULL)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO needradar_test_guard.identity "
                    "(singleton, guard_version, environment, database_name, guard_id, "
                    "guard_token_hash, created_at) VALUES "
                    "(TRUE, :version, :environment, :database, :guard_id, :token_hash, :created_at)"
                ),
                {
                    "version": GUARD_SCHEMA_VERSION,
                    "environment": GUARD_ENVIRONMENT,
                    "database": credential.database_name,
                    "guard_id": credential.guard_id,
                    "token_hash": token_hash,
                    "created_at": credential.created_at,
                },
            )
    finally:
        engine.dispose()


def bootstrap_test_database() -> SafeTestDatabase:
    settings = TestDatabaseEnvironment()
    _, host, port, database, _ = _safe_target_identity(
        test_database_url=settings.test_database_url,
        development_database_url=settings.database_url,
    )
    if not settings.test_database_admin_url:
        raise TestDatabaseSafetyError("TEST_DATABASE_ADMIN_URL is required for first bootstrap")
    admin_url = _parse_database_url(
        settings.test_database_admin_url, variable="TEST_DATABASE_ADMIN_URL"
    )
    admin_host, admin_port, admin_database = _identity(admin_url)
    if (admin_host, admin_port) != (host, port) or admin_database != "postgres":
        raise TestDatabaseSafetyError(
            "TEST_DATABASE_ADMIN_URL must target postgres on the dedicated local test server"
        )
    assert settings.test_database_url is not None
    if _database_exists(settings.test_database_admin_url, database):
        try:
            return validate_test_database_target(
                test_database_url=settings.test_database_url,
                development_database_url=settings.database_url,
            )
        except TestDatabaseSafetyError:
            raise TestDatabaseSafetyError(
                "Existing test database has no matching persistent and local guard; "
                "refusing automatic adoption"
            ) from None
    if LOCAL_GUARD_PATH.exists() or LOCAL_GUARD_PATH.is_symlink():
        raise TestDatabaseSafetyError(
            "Local test database guard already exists for a database that is absent"
        )
    credential = LocalGuardCredential(
        schema_version=GUARD_SCHEMA_VERSION,
        database_name=database,
        host=host,
        port=port,
        guard_id=str(uuid4()),
        guard_token=secrets.token_urlsafe(32),
        created_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )
    _create_database(settings.test_database_admin_url, database)
    _install_persistent_guard(settings.test_database_url, credential)
    _write_local_guard(credential)
    return validate_test_database_target(
        test_database_url=settings.test_database_url,
        development_database_url=settings.database_url,
    )


def safe_alembic_config(target: SafeTestDatabase) -> Config:
    config = Config(str(ALEMBIC_CONFIG_PATH))
    config.attributes["database_url"] = target.url
    return config


def prepare_test_database() -> SafeTestDatabase:
    target = assert_safe_test_database()
    command.upgrade(safe_alembic_config(target), "head")
    return target


def serve_e2e_api(*, port: int) -> None:
    target = assert_safe_test_database()
    os.environ["DATABASE_URL"] = target.url
    os.environ["NEEDRADAR_ENV_FILE"] = ""
    uvicorn.run(
        "needradar.main:app",
        host="127.0.0.1",
        port=port,
        log_level="info",
        log_config=uvicorn_log_config("INFO"),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NeedRadar test database safety boundary")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("bootstrap")
    subparsers.add_parser("verify")
    subparsers.add_parser("prepare")
    serve = subparsers.add_parser("serve-e2e")
    serve.add_argument("--port", type=int, default=18000)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    try:
        if args.command == "bootstrap":
            target = bootstrap_test_database()
            print(f"TEST_DATABASE_BOOTSTRAP: PASS {target.safe_identity}")
            return 0
        if args.command == "verify":
            target = assert_safe_test_database()
            print(f"TEST_DATABASE_GUARD: PASS {target.safe_identity}")
            return 0
        if args.command == "prepare":
            target = prepare_test_database()
            print(f"TEST_DATABASE_PREPARE: PASS {target.safe_identity}")
            return 0
        if args.command == "serve-e2e":
            serve_e2e_api(port=args.port)
            return 0
    except TestDatabaseSafetyError as exc:
        print(f"TEST_DATABASE_GUARD: FAIL {exc}", file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
