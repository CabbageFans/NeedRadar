# NeedRadar

NeedRadar 当前开发阶段是 **CHANGE-001 / C001-S1 Foundation**。

本阶段只提供可执行的本地 Web、FastAPI、PostgreSQL、Alembic、health/readiness、结构化日志和逻辑 Worker 边界。Research Project、Dashboard 业务、采集、Evidence、Signal、聚类、评分、机会与报告均尚未实现。

## Runtime contract

| Runtime | Required version / authority |
|---|---|
| Node.js | 24.x LTS (`.nvmrc`, `.node-version`, `engines`) |
| Package manager | pnpm 10.33.2 (`packageManager`, `pnpm-lock.yaml`) |
| Python | CPython 3.11.14 (`.python-version`) |
| Python dependencies | uv (`pyproject.toml`, `uv.lock`) |
| PostgreSQL | 18.6 official image, pinned digest |
| PostgreSQL driver | Psycopg 3 async only |

The host's global Python or npm packages are not part of the project runtime.

## Clean setup

Prerequisites: Node 24, Corepack, uv, and Docker Desktop/Engine with Compose.

```bash
corepack enable
pnpm install --frozen-lockfile
uv python install 3.11.14
uv sync --frozen --python 3.11
pnpm setup:e2e
cp .env.example .env
```

Replace the `change-me` placeholders in `.env`. The repository Docker defaults use local-only development credentials; a copied `.env` must use the matching values or explicitly configured alternatives. `.env` is ignored by Git.

`CORS_ORIGINS` uses one canonical JSON-array format, for example `CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]`. Do not convert it to a comma-separated string.

Only plain `http` origins whose host is `localhost` or `127.0.0.1` are accepted. Origins with credentials, paths, queries, fragments, wildcards, remote hosts, or HTTPS are rejected in Foundation.

## Database and migration

Start the local PostgreSQL 18 service and explicitly apply Alembic migrations:

```bash
pnpm db:up
pnpm db:migrate
```

Alembic is the schema authority. API startup and `/ready` never run migrations and the application never uses `Base.metadata.create_all()` as schema management.

The S1 migration is intentionally empty: the only database relation after migration is Alembic's own `alembic_version` metadata. No Research business table exists in S1.

## Start the Foundation

```bash
pnpm dev
```

- Web: <http://localhost:3000>
- API: <http://localhost:8000>
- Liveness: <http://localhost:8000/health>
- Readiness: <http://localhost:8000/ready>

Both applications bind to `127.0.0.1` by default. CORS permits only the explicitly configured local Web origins.

`/health` means only that the API process can serve HTTP. `/ready` performs a read-only PostgreSQL probe and requires the database Alembic revision to equal the application head. Missing, behind, divergent, unknown, or unavailable schema states return HTTP 503 and are never repaired automatically.

## Quality commands

```bash
pnpm check
pnpm test:unit
pnpm test:integration
pnpm test:migration
pnpm test:e2e
```

`setup:e2e` installs the Chromium binary declared by the pinned Playwright package. `test:integration`, `test:migration`, and `test:e2e` use only `TEST_DATABASE_URL` from the environment or copied `.env`; there is no fallback to `DATABASE_URL`. `pnpm db:test:up` starts the dedicated PostgreSQL server and runs the explicit first-use bootstrap. The bootstrap creates only a previously absent `needradar_test`/`needradar_test_*` database, installs a persistent `needradar_test_guard.identity` row, and writes a random matching credential to ignored `.needradar/test-db-guard.json`. An existing unguarded or mismatched database is never adopted, dropped, or reset. Every migration, integration, and E2E entry validates URL separation, strict naming, the persistent row, and the local credential before destructive schema work. Playwright exercises the real Browser → Web → FastAPI → PostgreSQL Foundation path.

When the default development ports are already occupied, verification may choose free local ports without changing the product defaults:

```bash
API_PORT=18123 WEB_PORT=31123 pnpm test:e2e
```

Both processes still bind only to `127.0.0.1`; absent overrides, Web remains 3000 and API remains 8000.

To stop local containers while preserving the guarded test database/container identity:

```bash
pnpm db:down
```

## Foundation worker seams

The backend identifies `crawler_worker`, `analysis_worker`, and `clustering_worker` as separate logical roles and task namespaces. All three deliberately have no handler in S1. No daemon, fake job, or future business output is created.
