from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[2]

FORBIDDEN_LOCKS = ["package-lock.json", "yarn.lock"]
FORBIDDEN_DRIVERS = ["asyncpg", "psycopg2"]
FORBIDDEN_DEPENDENCIES = ["kafka", "redis", "elasticsearch", "neo4j"]
FORBIDDEN_TABLE_PATTERNS = [
    r"create_table\(\s*[\"']research_project",
    r"create_table\(\s*[\"']crawl_job",
    r"create_table\(\s*[\"']evidence",
    r"create_table\(\s*[\"']demand_",
    r"create_table\(\s*[\"']opportunity",
    r"create_table\(\s*[\"']model_run",
]


def fail(message: str) -> None:
    raise SystemExit(f"S1 scope audit failed: {message}")


for lock in FORBIDDEN_LOCKS:
    if (ROOT / lock).exists():
        fail(f"competing lockfile exists: {lock}")

manifest_text = "\n".join(
    (ROOT / name).read_text()
    for name in ("package.json", "pyproject.toml", "pnpm-lock.yaml")
    if (ROOT / name).exists()
).lower()
for dependency in FORBIDDEN_DRIVERS + FORBIDDEN_DEPENDENCIES:
    if re.search(rf"(^|[^a-z0-9_-]){re.escape(dependency)}([^a-z0-9_-]|$)", manifest_text):
        fail(f"forbidden dependency present: {dependency}")

migration_text = "\n".join(
    path.read_text() for path in (ROOT / "apps/api/migrations/versions").glob("*.py")
)
for pattern in FORBIDDEN_TABLE_PATTERNS:
    if re.search(pattern, migration_text, re.IGNORECASE):
        fail(f"future business table detected: {pattern}")

web_sources = "\n".join(
    path.read_text(errors="ignore")
    for base in (ROOT / "apps/web/app", ROOT / "apps/web/src")
    for path in base.rglob("*")
    if path.is_file()
)
if re.search(r"from\s+[\"']needradar", web_sources):
    fail("frontend imports backend runtime package")
if re.search(r"NEXT_PUBLIC_[A-Z0-9_]*(SECRET|PASSWORD|TOKEN|KEY)", web_sources):
    fail("client-visible secret environment variable detected")

ignored = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=ROOT, check=False).returncode
if ignored != 0:
    fail(".env is not ignored")

result = {
    "status": "PASS",
    "business_tables": [],
    "competing_locks": [],
    "competing_drivers": [],
    "future_infrastructure": [],
    "frontend_backend_imports": [],
    "client_secret_names": [],
}
print(json.dumps(result, indent=2))
