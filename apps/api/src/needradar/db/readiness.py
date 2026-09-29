from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine


@dataclass(frozen=True, slots=True)
class ReadinessResult:
    ready: bool
    database: str
    schema: str
    detail: str
    revision: str | None = None


class ReadinessService:
    def __init__(self, *, engine: AsyncEngine, alembic_config_path: Path) -> None:
        self._engine = engine
        self._alembic_config_path = alembic_config_path

    def _application_head(self) -> tuple[str, set[str]]:
        config_path = self._alembic_config_path.resolve()
        config = Config(str(config_path))
        script_location = config.get_main_option("script_location")
        if script_location is None:
            raise RuntimeError("Alembic script_location is missing")
        if not Path(script_location).is_absolute():
            config.set_main_option(
                "script_location", str((config_path.parent / script_location).resolve())
            )
        scripts = ScriptDirectory.from_config(config)
        heads = scripts.get_heads()
        if len(heads) != 1:
            raise RuntimeError("NeedRadar requires exactly one Alembic head")
        known = {revision.revision for revision in scripts.walk_revisions()}
        return heads[0], known

    async def check(self) -> ReadinessResult:
        try:
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
                table_name = await connection.scalar(
                    text("SELECT to_regclass('public.alembic_version')")
                )
                if table_name is None:
                    return ReadinessResult(
                        ready=False,
                        database="ok",
                        schema="missing",
                        detail="Database is reachable but Alembic metadata is missing.",
                    )
                revision_rows = await connection.execute(
                    text("SELECT version_num FROM alembic_version")
                )
                revisions = cast(list[str], revision_rows.scalars().all())
        except (SQLAlchemyError, OSError):
            return ReadinessResult(
                ready=False,
                database="unavailable",
                schema="unknown",
                detail="PostgreSQL is unavailable.",
            )

        try:
            head, known = self._application_head()
        except (OSError, RuntimeError):
            return ReadinessResult(
                ready=False,
                database="ok",
                schema="application-graph-invalid",
                detail="Application migration graph is not a single valid head.",
            )

        if len(revisions) == 0:
            return ReadinessResult(
                ready=False,
                database="ok",
                schema="behind",
                detail="Database schema is behind the application head.",
            )
        if len(revisions) != 1:
            return ReadinessResult(
                ready=False,
                database="ok",
                schema="divergent",
                detail="Database schema revision is divergent.",
            )

        revision = revisions[0]
        if revision == head:
            return ReadinessResult(
                ready=True,
                database="ok",
                schema="head",
                detail="PostgreSQL and schema are ready.",
                revision=revision,
            )
        if revision in known:
            return ReadinessResult(
                ready=False,
                database="ok",
                schema="behind",
                detail="Database schema is behind the application head.",
                revision=revision,
            )
        return ReadinessResult(
            ready=False,
            database="ok",
            schema="unknown",
            detail="Database schema revision is unknown to the application.",
            revision=revision,
        )
