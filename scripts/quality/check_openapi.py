from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "scripts/quality"))

from export_openapi import render_schema  # noqa: E402

schema_path = ROOT / "apps/api/openapi.json"
types_path = ROOT / "apps/web/src/lib/api/generated/schema.ts"

if schema_path.read_text() != render_schema():
    raise SystemExit("OpenAPI snapshot is stale; run pnpm generate:openapi")

with tempfile.TemporaryDirectory(prefix="needradar-openapi-") as temp_dir:
    generated = Path(temp_dir) / "schema.ts"
    subprocess.run(
        [
            "pnpm",
            "exec",
            "openapi-typescript",
            str(schema_path),
            "-o",
            str(generated),
        ],
        cwd=ROOT,
        check=True,
    )
    if types_path.read_text() != generated.read_text():
        raise SystemExit("Generated Web API types are stale; run pnpm generate:openapi")

print("OpenAPI snapshot and generated Web types are current")
