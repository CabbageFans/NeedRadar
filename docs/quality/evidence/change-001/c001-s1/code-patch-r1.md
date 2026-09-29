# C001-S1 Code Patch R1 Evidence

> Historical R1 record. Its session-controlled database marker was rejected by Independent Code Review R2 and is not current authorization evidence. The persistent database guard plus matching local credential and the current verification results are documented in `verification.md`.

- Executed: `2026-09-28T10:27:19+08:00`
- Branch: `main`
- HEAD: `9b48714a90bb29aadf29a78e51be1a479b3ffd5a`
- Scope: Independent Code Review R1 BLOCKER/HIGH findings only
- Verification stage: `CODE_REVIEW_READY`
- Requirement result policy: D-015; no Requirement is marked `PASS`

## Runtime

| Tool | Version |
|---|---|
| Node.js | `v24.15.0` |
| pnpm | `10.33.2` |
| uv | `0.12.2` |
| Python | `3.11.14` |
| PostgreSQL | `18.6` dedicated `postgres-test` service |

## Patch verification

| Command / check | Exit | Result |
|---|---:|---|
| `pnpm install --frozen-lockfile` | 0 | Locked Node dependency graph is current. |
| `uv sync --frozen --python 3.11.14` | 0 | Locked Python dependency graph is current. |
| `pnpm check` | 0 | Web lint/typecheck/Vitest/build, backend formatting/lint/mypy, OpenAPI, scope and quality checks pass. |
| `pnpm test:unit` | 0 | Backend 29 passed; Web 1 passed. SAFE-DB-001..007, clean env-file and QUALITY-001..006 are included. |
| `pnpm test:integration` | 0 | 9 passed against PostgreSQL 18.6: two database-safety, one migration and six readiness tests. |
| `pnpm test:migration` | 0 | Empty baseline downgrade/upgrade round trip passed after shared guard validation. |
| `pnpm test:e2e` | 0 | Real Browser → Web → guarded FastAPI → PostgreSQL path passed; preparation and API startup both used the shared Python guard. |
| `openspec validate foundation --strict` | 0 | Change is valid. |
| `git diff --check` | 0 | No whitespace error. |

## Database safety evidence

The only authority is `needradar.testing.database_safety`. Destructive test automation requires all of:

1. a non-empty `TEST_DATABASE_URL` with no `DATABASE_URL` fallback;
2. Psycopg 3 and the dedicated local test endpoint;
3. database name `needradar_test` or `needradar_test_*`, excluding protected databases;
4. a target different from `DATABASE_URL` when it is declared;
5. PostgreSQL database setting `needradar.environment=TEST`, installed only by the dedicated `postgres-test` bootstrap.

The real-PostgreSQL rejection test snapshots the protected `postgres` database's public tables and database catalog, invokes the validator, and confirms both snapshots remain identical after refusal. Error tests assert passwords never appear in validation messages.

## Environment contract evidence

`CORS_ORIGINS` has one canonical JSON-array representation. The clean env-file unit test copies `.env.example`, replaces only the documented password placeholders, loads it through `load_settings()`, constructs the real FastAPI app, verifies both local origins by CORS preflight, and confirms credentials/placeholders are absent from health and OpenAPI client-visible output.

An additional direct load of `.env.example` completed with the expected local origins and `127.0.0.1:8000`; no manual CORS rewrite was required.

## Traceability gate evidence

The five premature results were reverted from `PASS` to `UNIMPLEMENTED`: `REQ-ARCH-002`, `REQ-ARCH-010`, `REQ-ARCH-013`, `REQ-GOVERNANCE-011`, and `REQ-FOUNDATION-001`.

`docs/quality/VERIFICATION_STATE.json` records `CODE_REVIEW_READY`, current Slice `C001-S1`, D-015 result-update authority `C001-S6`, and no independent Requirement Verification evidence. The checker fixtures prove implementation and code-review stages reject PASS, `IMPLEMENTED_UNVERIFIED` is syntactically allowed, verified-stage PASS requires both the authorized Slice and an existing independent evidence artifact, cross-Change partial coverage cannot PASS, and missing evidence paths fail.

No Requirement Verification was performed in this patch.
