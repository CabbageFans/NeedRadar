# C001-S1 Verification Evidence

- Executed: `2026-09-28T14:33:08+08:00`
- Branch: `main`
- HEAD before implementation: `9b48714a90bb29aadf29a78e51be1a479b3ffd5a`
- Scope: CHANGE-001 / C001-S1 only
- Final result: implementation verification PASS, ready for independent code review R3; no Requirement is marked PASS

## Runtime and locked setup

| Command | Exit | Evidence |
|---|---:|---|
| `pnpm install --frozen-lockfile` | 0 | Lockfile current; pnpm 10.33.2 used. |
| `uv sync --frozen --python 3.11.14` | 0 | 41 declared packages checked; repository `.venv` uses CPython 3.11.14. |
| `pnpm setup:e2e` | 0 | Pinned Playwright Chromium runtime is declared and installable from the repository command. |
| `node --version` | 0 | `v24.15.0` |
| `pnpm --version` | 0 | `10.33.2` |
| `uv run python --version` | 0 | `Python 3.11.14` |
| `uv --version` | 0 | `uv 0.12.2` |
| `uv run python -c 'import psycopg; print(psycopg.__version__)'` | 0 | `3.3.6`; Psycopg 3 is the sole PostgreSQL driver family. |
| `docker compose exec -T postgres-test postgres --version` | 0 | `PostgreSQL 18.6 (Debian 18.6-1.pgdg12+2)` |

The PostgreSQL image is `postgres:18.6-bookworm@sha256:3725f4e2499eef5134592b3b4ab79a543ed7f8e533b05b5b637af926630f6650`. The only declared PostgreSQL driver family is Psycopg 3 (`psycopg[binary]`); the audit found no `asyncpg` or `psycopg2`, no `package-lock.json`, and no `yarn.lock`.

## Static and unit verification

| Command | Exit | Evidence |
|---|---:|---|
| `pnpm check` | 0 | Web ESLint/typecheck/Vitest/build, Ruff format/lint, mypy, OpenAPI drift, secret/import/scope audits, and quality-document validation all passed. |
| `pnpm test:unit` | 0 | Backend: 54 passed under pytest-asyncio `Mode.STRICT`; Web: 1 passed. DB-SAFE-001..010 and QG-001..010 include the required safety/evidence bypass attempts. |
| `pnpm --filter @needradar/web build` (within `pnpm check`) | 0 | Next.js 15.5.26 production build compiled; `/`, `/_not-found`, `/dashboard` generated. |
| `pnpm check:openapi` (within `pnpm check`) | 0 | FastAPI schema snapshot and generated Web TypeScript types match. |
| `pnpm check:scope` (within `pnpm check`) | 0 | No future business table, competing lock/driver, future infrastructure, backend import in frontend, or client secret name. |

## PostgreSQL, migration, and readiness verification

| Command | Exit | Evidence |
|---|---:|---|
| `pnpm test:integration` | 0 | 11 passed against isolated PostgreSQL 18.6: persistent/local guard, forged session-option refusal, unsafe-target preservation, migration, READY-001..005, engine disposal, and real Uvicorn JSON startup/access logs. |
| `pnpm test:migration` | 0 | 1 passed: clean/base → upgrade head → downgrade base → re-upgrade head. |
| `psql ... select version_num from alembic_version` | 0 | `20260928_0001` |
| `psql ... pg_tables where schemaname='public'` | 0 | Only `alembic_version`; no business table. |

Readiness cases executed:

- DB alive + revision head → HTTP 200, `status=ready`, `database=ok`, `schema=head`.
- DB unavailable → `/ready` HTTP 503 with `SERVICE_NOT_READY`; `/health` remains HTTP 200.
- DB reachable with empty known revision state → HTTP 503, `schema=behind`.
- DB reachable with unknown revision → HTTP 503, `schema=unknown`.
- DB reachable with divergent revision rows → HTTP 503, `schema=divergent`.
- DB reachable with missing Alembic metadata → HTTP 503, `schema=missing`.

Readiness response tests cover the defined database/revision states; source inspection confirms the readiness implementation contains only queries. Migration happens only through the explicit Alembic command; application code contains no `create_all` call.

## E2E and governance verification

| Command | Exit | Evidence |
|---|---:|---|
| `API_PORT=18123 WEB_PORT=31123 pnpm test:e2e` | 0 | 1 Playwright test passed in Chromium using real Web → FastAPI → PostgreSQL 18 on alternate local-only ports. Product defaults remain Web 3000 / API 8000. |
| `openspec validate foundation --strict` | 0 | `Change 'foundation' is valid`. |
| `uv run python scripts/quality/check_quality_docs.py` | 0 | PASS: 222 Requirements, 211 acceptance entries, 15 red lines; no quality-doc consistency failure. |
| `git diff --check` | 0 | No whitespace errors. |

Playwright verified the real Foundation page, API liveness, database/schema readiness, revision `20260928_0001`, and explicit copy that Research Project and downstream research capabilities are not implemented. No API mock was used.

The authoritative database validator requires an explicit strict-name `TEST_DATABASE_URL`, separation from `DATABASE_URL`, a persistent `needradar_test_guard.identity` row, a matching ignored local random credential, and agreement with `current_database()`. It rejects a missing local guard, mismatched guard, protected/unsafe name, development URL, and forged libpq session option before destructive work. The protected-database preservation integration test proves rejection leaves its tables and database catalog unchanged.

The quality checker accepts Requirement `PASS` only with a non-empty JSON manifest below `docs/quality/evidence/`, real repository-bound implementation/test/artifact files, full AC/stage/gate/command fields, zero command exit codes, and a recomputed aggregate source fingerprint. External, empty, arbitrary, symlink-escaping, missing-ref, stale-fingerprint, and stage-only bypasses fail.

## Non-blocking warnings

- FastAPI/Starlette emits one test-only deprecation warning about its `TestClient` compatibility layer; all assertions pass and production runtime is unaffected.
- Playwright child processes emit `NO_COLOR`/`FORCE_COLOR` warnings; the browser journey passes.

No failing final test remains. No test was skipped, xfailed, deleted, weakened, or replaced with SQLite/mock acceptance. The five fully implemented S1 rows are `IMPLEMENTED_UNVERIFIED`; partial/cross-stage rows remain `UNIMPLEMENTED`.
