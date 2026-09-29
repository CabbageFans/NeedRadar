# Tasks

## C001-S1

### Executable Product Boundary & Health

- [x] 1.1 Establish the reproducible root workspace and dependency/runtime contract.
  - **Objective:** Create the monorepo directories; pin Node.js 24.x LTS through `.nvmrc`, `.node-version`, and engines, an exact pnpm `packageManager` and sole `pnpm-lock.yaml`; pin Python 3.11.x with uv, `pyproject.toml`, `uv.lock`, and `.python-version`; declare PostgreSQL 18.x and Psycopg 3 async; add `.env.example`, root scripts, ignore rules, and startup/test command documentation.
  - **Files / area:** Root manifests and README; `apps/web`; `apps/api`; `tests/e2e`; no domain implementation.
  - **Requirements:** REQ-FOUNDATION-001; REQ-ARCH-002/010 at `SHOULD`; REQ-PROJECT-002 partial.
  - **Acceptance:** AC-FOUNDATION-001; AC-PROJECT-002 remains `PARTIAL COVERAGE / FUTURE COMPLETION`.
  - **Implementation constraints:** Do not add login, SaaS hosting, analytics, future routes, SQLite, npm/yarn lockfiles, asyncpg/psycopg2, Node 26 Current, global pip/npm state, or Python 3.14 support. Unit tests do not read developer `.env`; integration/E2E require isolated `TEST_DATABASE_URL` and never the ordinary development database.
  - **Verification:** From a clean checkout, validate runtime declarations and sole lock/driver authorities; run locked install/config commands; verify pytest + pytest-asyncio `strict`, PostgreSQL 18, and no undeclared global package/config.
  - **Done condition:** A reviewer can reproduce exact Node/pnpm/Python/uv/PostgreSQL/driver/test prerequisites from repository files and finds no competing package manager, lockfile, driver, or implicit machine state.

- [x] 1.2 Build the FastAPI process boundary, PostgreSQL lifecycle, health/readiness, and structured Problem Details foundation.
  - **Objective:** Add configuration, app factory/lifespan, Psycopg 3 async SQLAlchemy engine/session ownership, `GET /health`, read-only `GET /ready` connectivity + exact Alembic-head checks, request IDs, structured errors, and safe shutdown.
  - **Files / area:** `apps/api/src/needradar/{api,core,db}` and S1 API unit/integration tests.
  - **Requirements:** REQ-FOUNDATION-001; REQ-ARCH-012 partial; structured-error user contract.
  - **Acceptance:** AC-FOUNDATION-001; AC-ARCH-012 remains partial.
  - **Implementation constraints:** `/health` performs no dependency query; `/ready` runs a lightweight real PostgreSQL query and requires database revision exactly equal to application head; readiness never migrates or calls `create_all`; responses/logs expose no credentials or stack traces.
  - **Verification:** Run unit/static checks and real PostgreSQL 18 READY-001..005 integration cases: DB+head ready; DB unavailable not-ready; schema behind not-ready; missing/divergent/unknown revision not-ready; `/health` still 200 while DB is unavailable; verify engine disposal.
  - **Done condition:** Liveness is process-only and readiness is read-only DB+schema-head truth under every defined failure mode.

- [x] 1.3 Establish Alembic mechanics without a Research business table.
  - **Objective:** Configure async-aware Alembic and create an empty Foundation baseline revision that proves migration authority before Project schema work.
  - **Files / area:** `apps/api/alembic.ini`, `apps/api/migrations`, migration test helpers.
  - **Requirements:** REQ-GOVERNANCE-011; REQ-FOUNDATION-001.
  - **Acceptance:** AC-GOVERNANCE-011, AC-FOUNDATION-001.
  - **Implementation constraints:** S1 MUST NOT create `research_project` or any future business table; manual SQL and application `create_all` are not the normal path.
  - **Verification:** On an isolated PostgreSQL 18 database run clean DB → `alembic upgrade head`, assert exact revision, then the defined baseline downgrade → upgrade and inspect the catalog; verify only Alembic metadata exists and readiness reports non-head states as 503.
  - **Done condition:** Migration commands are repeatable, tested, and ready for S2 schema without any business-table leakage.

- [x] 1.4 Establish the Web shell, API access boundary, static quality commands, logical worker registry, and structured logging schema.
  - **Objective:** Add the minimal real Dashboard shell/API reachability, typed API-layer location, localhost/CORS/secret boundary, JSON logging fields, and identifiable `crawler_worker`/`analysis_worker`/`clustering_worker` roles.
  - **Files / area:** `apps/web`, `apps/api/src/needradar/{core,workers}`, root scripts, S1 tests/docs.
  - **Requirements:** REQ-ARCH-001; REQ-ARCH-003 partial; REQ-ARCH-011/012 partial; REQ-ARCH-013 `MAY`; REQ-RESILIENCE-007 partial; REQ-RESILIENCE-008 `MAY`.
  - **Acceptance:** AC-ARCH-001; AC-ARCH-003/011/012 and AC-RESILIENCE-007 only partial.
  - **Implementation constraints:** Default Web/API bind is `127.0.0.1` at documented localhost URLs; CORS lists only explicit local origins, never `*`; secrets are backend-only and absent from `NEXT_PUBLIC_*`, bundles, API/SSE, browser storage, tracked `.env`, and logs. Worker roles have no handlers/daemons/fake jobs; `job_id=null`; no Redux/Zustand, future business page, or mock API may satisfy S1.
  - **Verification:** Run Web lint/format/typecheck, dependency/import/bundle audit for AC-ARCH-001, secret/static configuration scan, bind/CORS tests, backend log-shape and worker-registry tests, OpenAPI diff, and a browser smoke test that real localhost Web reaches real API.
  - **Done condition:** AC-ARCH-001 has Foundation-scope STATIC evidence that crawler process core, LLM judgment, clustering, scoring, backend runtime packages, and secrets do not enter the client; global Requirement remains `UNIMPLEMENTED` for future Changes.

- [x] 1.5 Execute and retain the C001-S1 Exit Gate.
  - **Objective:** Prove a clean environment starts pinned/local-only Web + API + PostgreSQL 18 and distinguishes liveness from DB+schema readiness.
  - **Files / area:** S1 evidence directory and startup runbook only.
  - **Requirements:** REQ-FOUNDATION-001.
  - **Acceptance:** AC-FOUNDATION-001.
  - **Implementation constraints:** Real PostgreSQL is mandatory; manifests reference only repository-controlled verification target IDs. The trusted runner records real argv, timestamps, process exit codes, output hashes, structured test bindings, and source/target fingerprints; manifest command/exit/log/reviewer claims are non-authoritative. No later capability is claimed.
  - **Verification:** Repeat locked install/start/explicit migrate/READY-001..005/browser smoke and architecture/secret audit through canonical targets; run `openspec validate foundation --strict` plus quality-doc validation and the R5 adversarial suite.
  - **Done condition:** Retained, runner-generated S1 receipts prove the fixed runtime/local/secret/readiness contract; every existing IU is freshly revalidated with no persisted-state exception; catalog confirms no Research/future business table exists; no Project restart-persistence claim is made in S1.

## C001-S2

### Empty Research Project Persistence

- [ ] 2.1 Add the minimal `research_project` Alembic migration and SQLAlchemy mapping.
  - **Objective:** Create exactly the D-007 fields, CHECK constraints, UTC types, UUIDv4 mapping, and Foundation indexes.
  - **Files / area:** `apps/api/migrations/versions`, `apps/api/src/needradar/projects` persistence model, catalog tests.
  - **Requirements:** REQ-DATA-001; REQ-GOVERNANCE-011; REQ-PROJECT-008 partial.
  - **Acceptance:** AC-DATA-001, AC-GOVERNANCE-011; AC-PROJECT-008 remains partial.
  - **Implementation constraints:** One business table only; no metadata/error JSON or future tables; migration is reversible and application startup never creates schema.
  - **Verification:** Fresh PostgreSQL upgrade/catalog assertions, constraint negative tests, downgrade to baseline, and re-upgrade.
  - **Done condition:** The exact Foundation schema round-trips through Alembic and all future-domain table names are absent.

- [ ] 2.2 Implement Project create/list/get/Snapshot through repository and application service boundaries.
  - **Objective:** Add strict request/response schemas, UUID/UTC serialization, active-only deterministic queries, derived Foundation progress, and 422/404 Problem Details.
  - **Files / area:** `apps/api/src/needradar/projects`, Project routers, generated OpenAPI/client types, S2 unit/integration tests.
  - **Requirements:** REQ-PROJECT-013; REQ-DATA-001; REQ-SSE-001 partial through Snapshot.
  - **Acceptance:** AC-PROJECT-013, AC-DATA-001; AC-SSE-001 completes only in S5.
  - **Implementation constraints:** Client lifecycle fields/unknown fields reject; initial status/version are backend-owned; Snapshot has no fake counts; repository does not commit.
  - **Verification:** Unit-test validation/serialization/progress; PostgreSQL integration-test valid/invalid create, deterministic list, get, missing ID, and committed row contents.
  - **Done condition:** API contract and database assertions prove a real empty Project is created, listed, retrieved, and Snapshotted from PostgreSQL.

- [ ] 2.3 Implement optimistic soft delete without purge or cascade.
  - **Objective:** Require `If-Match`, compare-and-swap version, set `deleted_at`/`updated_at`, preserve status/row, and filter deleted Projects from ordinary list/get/Snapshot.
  - **Files / area:** Project application/repository/router, Problem Details mappings, S2 tests and API docs.
  - **Requirements:** REQ-PROJECT-018 (CHANGE-001 partial); REQ-PROJECT-013; DEC-007.
  - **Acceptance:** AC-PROJECT-018 partial Project-only evidence; AC-PROJECT-013. Full AC-PROJECT-018 remains `UNIMPLEMENTED` until CHANGE-003.
  - **Implementation constraints:** No physical delete, Restore, PURGE, Source Content/Comment, Evidence, Project-Source join table, fake Source fixture, or cascade; deleted and unknown ordinary get both 404; stale version 409 and missing precondition 428.
  - **Verification:** Unit-test filter/version rules; PostgreSQL integration-test Project row preservation, version +1, list/get exclusion, repeated delete 404/no second mutation, stale conflict, and schema audit proving no Source-domain table. Do not claim shared-Source retention evidence.
  - **Done condition:** Project-owned soft delete semantics match DEC-007; retained result is explicitly `PARTIAL COVERAGE`, and shared-Source clauses remain for CHANGE-003 real PostgreSQL verification.

- [ ] 2.4 Prove PostgreSQL persistence across API process restart and retain the C001-S2 Exit Gate evidence.
  - **Objective:** Exercise migrated schema and Project CRUD/deletion across two API process lifetimes using the same database.
  - **Files / area:** Integration harness, S2 runbook/evidence.
  - **Requirements:** REQ-FOUNDATION-001, REQ-DATA-001, REQ-PROJECT-013; REQ-PROJECT-018 partial.
  - **Acceptance:** AC-FOUNDATION-001, AC-DATA-001, AC-PROJECT-013; AC-PROJECT-018 partial Project-only evidence.
  - **Implementation constraints:** No in-memory/fixture reconstruction and no SQLite evidence.
  - **Verification:** Create and mutate in process A, restart as process B, assert list/get/Snapshot/deleted filtering and exact version/timestamps; retain catalog and API reports.
  - **Done condition:** S2 evidence proves Project persistence/restart/soft delete; AC-PROJECT-008 and AC-PROJECT-018 are explicitly recorded partial/`UNIMPLEMENTED`, never PASS.

## C001-S3

### Backend-Owned Project State

- [ ] 3.1 Implement the data-defined 13-state vocabulary, named commands, and central transition policy.
  - **Objective:** Encode the D-009 production transition definition for the state service and separately hand-author an independent expected transition oracle from DEC-006/capability/Acceptance.
  - **Files / area:** `apps/api/src/needradar/projects` domain/application policy and S3 unit tests.
  - **Requirements:** REQ-PROJECT-009/010/016; DEC-003/006.
  - **Acceptance:** AC-PROJECT-010/016, AC-GOVERNANCE-014.
  - **Implementation constraints:** Exact vocabulary; no general target setter; no future Planner/Crawl/Analysis work; same-state is no transition; Stop alias shares only confirmed cancellation semantics. Test `EXPECTED_ALLOWED_TRANSITIONS`/`EXPECTED_FORBIDDEN_TRANSITIONS` MUST NOT import, call, reflect, serialize, or derive from production policy.
  - **Verification:** Static dependency audit proves oracle separation; take all 169 source/target pairs from the status vocabulary, ask the independent test oracle for allowed/forbidden, then invoke production behavior and include command/precondition mismatch negatives.
  - **Done condition:** Independent exhaustive expectations agree with production behavior for all 169 pairs and static ownership tests find no unrestricted repository/API status mutation or self-proving test dependency.

- [ ] 3.2 Implement failure-source retry, terminal rules, completion time, and atomic version compare-and-swap.
  - **Objective:** Persist `failed_from_status`, restrict retry to its stored source, clear it on retry, enforce CANCELLED/READY rules, and increment version exactly once after valid observable mutation.
  - **Files / area:** State application service/repository update path, database constraints, S3 tests.
  - **Requirements:** REQ-PROJECT-017; REQ-SSE-002 version semantics; DEC-006/008.
  - **Acceptance:** AC-PROJECT-017, AC-SSE-002 partial until S5 event contract.
  - **Implementation constraints:** Failure allowed only from the five D-009 sources; delete remains separate; rolled-back/rejected/no-op commands consume no version.
  - **Verification:** Independent table-driven unit tests for every failure source/retry, READY/CANCELLED terminal behavior, arbitrary target, same-state, repeated command, optimistic-version replay, and soft-deleted Project rejection; PostgreSQL CAS concurrency test with one winner/one 409; constraint/rollback assertions.
  - **Done condition:** Failure, retry, terminal, completion timestamp, and version behaviors persist atomically and reject client-selected targets.

- [ ] 3.3 Add the backend application command port and test-only driver without a production arbitrary-state API.
  - **Objective:** Provide future Changes and E2E fixtures a named-command entry that always invokes the state service.
  - **Files / area:** Project application ports; test app factory/driver; OpenAPI ownership tests.
  - **Requirements:** REQ-PROJECT-010/011/016/017; REQ-ARCH-012 partial.
  - **Acceptance:** AC-PROJECT-010/011/016/017; AC-ARCH-012 partial.
  - **Implementation constraints:** Test driver absent from production routes/OpenAPI; it accepts command + expected version, never target status; no direct database setup for E2E state changes.
  - **Verification:** Static/OpenAPI negative tests plus integration calls proving driver and future port share the same policy/conflict behavior.
  - **Done condition:** Authoritative transitions can be exercised end to end for testing without exposing or implementing future product actions.

- [ ] 3.4 Execute and retain the C001-S3 Exit Gate.
  - **Objective:** Aggregate state-policy, persistence, conflict, and ownership evidence.
  - **Files / area:** S3 evidence and Requirement-to-test matrix.
  - **Requirements:** REQ-PROJECT-010/016/017; REQ-GOVERNANCE-014.
  - **Acceptance:** AC-PROJECT-010/016/017, AC-GOVERNANCE-014.
  - **Implementation constraints:** Every allowed and forbidden transition must be represented; failures cannot be waived or converted to expected skips.
  - **Verification:** Run static, complete unit matrix, and PostgreSQL state/version suite; retain machine-readable pair coverage and test results.
  - **Done condition:** Evidence accounts for all 169 independently expected pairs, every failure retry source, arbitrary/repeated/unchanged/deleted negatives, READY/CANCELLED terminal behavior, and PostgreSQL persistence with zero unexplained cases.

## C001-S4

### Dashboard Project Journey

- [ ] 4.1 Implement the typed Web API layer and Foundation routes.
  - **Objective:** Generate/typecheck API types and add `/dashboard`, `/research/new`, `/research/[projectId]`, shared error handling, and root redirect.
  - **Files / area:** `apps/web/app`, `apps/web/src/lib/api`, Web tests; generated client schema.
  - **Requirements:** REQ-PROJECT-011/014; REQ-ARCH-011/012 partial.
  - **Acceptance:** AC-PROJECT-011/014; AC-ARCH-011/012 partial.
  - **Implementation constraints:** Server Components read; Client Components mutate/live-update; no future route shells, localStorage facts, hardcoded projects, or mock final path.
  - **Verification:** Web format/lint/typecheck, generated schema diff, route/component unit tests, and API Problem Details rendering tests.
  - **Done condition:** All Foundation pages compile against the real OpenAPI contract and no component performs an unowned ad hoc domain request.

- [ ] 4.2 Implement real Dashboard create/list/get/delete/detail behavior and unavailable-metric semantics.
  - **Objective:** Let the user create an empty Project, see backend fields/progress/update time, enter its detail, and soft-delete it from ordinary view.
  - **Files / area:** Dashboard/new/detail components and client reducers; Web unit tests and UX copy.
  - **Requirements:** REQ-PROJECT-011/014; REQ-PROJECT-018 and REQ-UI-002 partial.
  - **Acceptance:** AC-PROJECT-011/014; AC-PROJECT-018 Project/Dashboard subset and AC-UI-002 remain partial.
  - **Implementation constraints:** Backend status/version wins; Cluster/Evidence/Top Demand/platform coverage hidden or “尚未分析”/`—`, never fake `0`; deleted direct URL follows backend 404.
  - **Verification:** Component tests for API-error/state/unavailable metrics; integration assertions that rendered data matches PostgreSQL-backed API responses.
  - **Done condition:** Dashboard contains only real Project facts and never implies downstream analysis has run.

- [ ] 4.3 Implement Playwright Journey 1 and Journey 2 against the real stack and retain the C001-S4 Exit Gate.
  - **Objective:** Prove empty-project creation/status and soft-delete disappearance through Web → API → PostgreSQL.
  - **Files / area:** `tests/e2e`, E2E database harness, S4 evidence.
  - **Requirements:** REQ-PROJECT-011/013/014; REQ-PROJECT-018 partial.
  - **Acceptance:** AC-PROJECT-011/013/014; AC-PROJECT-018 partial Project/UI evidence only.
  - **Implementation constraints:** Real FastAPI and migrated PostgreSQL; mocks allowed only in separate unit tests; browser local state cannot seed business facts.
  - **Verification:** Journey 1: Dashboard → create → Dashboard → persisted card → correct backend status. Journey 2: create → soft delete → Dashboard absent plus PostgreSQL row retained. Add a backend/client conflict fixture proving backend display wins.
  - **Done condition:** Playwright traces and Project database assertions are retained and both journeys pass from isolated migrated PostgreSQL; no shared-Source retention or full AC-PROJECT-018 PASS is claimed.

## C001-S5

### Project Progress Event Foundation

- [ ] 5.1 Implement post-commit PostgreSQL notification publishing and bounded SSE subscriptions.
  - **Objective:** Add four mutation event types plus `STREAM_READY`/`HEARTBEAT` control contracts, transaction-scoped `pg_notify`, dedicated listener, Project-specific stream, 15-second configurable heartbeat, bounded queues, and cleanup.
  - **Files / area:** API event module/routers/lifecycle; Project services; S5 backend tests.
  - **Requirements:** REQ-SSE-001..004; REQ-API-007 partial; REQ-RESILIENCE-006 `SHOULD` subset.
  - **Acceptance:** AC-SSE-001..004; AC-API-007 partial.
  - **Implementation constraints:** Mutation `project_version` equals committed database version; `event_id` is transport identity only. `STREAM_READY` and heartbeat carry `connection_id`/`observed_project_version`, never advance or claim mutation `project_version`. No event table/outbox/replay/Event Sourcing/Kafka/Redis/future event types; SSE holds no ORM transaction.
  - **Verification:** Real PostgreSQL contract/integration tests for mutation/control schemas, post-commit vs rollback, version order, consecutive heartbeat/control non-mutation, ready-after-subscribe ordering, missing/deleted Project, delete-then-close, overflow, disconnect, and shutdown cleanup.
  - **Done condition:** PostgreSQL delivers only committed mutation notifications, control events never change Project version, subscription readiness is explicit, and every connection resource is bounded/released.

- [ ] 5.2 Implement Connect/Buffer/Snapshot/Reconcile client and deterministic race coverage.
  - **Objective:** Add typed EventSource ownership, `STREAM_READY`-gated handshake buffer, per-Project version reducer, Snapshot reconciliation, stale/duplicate/malformed handling, and bounded full-handshake recovery.
  - **Files / area:** `apps/web/src/lib/events`, Dashboard/detail client components, Web unit tests.
  - **Requirements:** REQ-SSE-001/003/004; REQ-PROJECT-011.
  - **Acceptance:** AC-SSE-001/003/004, AC-PROJECT-011.
  - **Implementation constraints:** Open stream → wait `STREAM_READY` → buffer → GET Snapshot → discard versions `<= snapshot` → reconcile higher versions → live. On any disconnect close/discard and repeat the complete handshake. Never directly trust event payload as Project truth; no Last-Event-ID replay. Race tests use deterministic barriers, synchronization primitives, test hooks, or a controlled fake transport boundary—never sleeps for ordering.
  - **Verification:** Automate RACE-001 mutation before ready; RACE-002 after ready/before Snapshot request; RACE-003 during blocked Snapshot; RACE-004 after Snapshot response/before drain; RACE-005 disconnect during handshake; RACE-006 duplicate; RACE-007 stale/equal. Also cover malformed/unknown, failed Snapshot, capped backoff, unmount cleanup, and only non-older REST adoption.
  - **Done condition:** All seven controlled race cases pass, `project_version <= currentVersion` never re-applies state, and every initial/reconnect path completes the same race-free handshake.

- [ ] 5.3 Implement Playwright Journey 3 and Journey 4 against real SSE/PostgreSQL and retain the C001-S5 Exit Gate.
  - **Objective:** Prove live backend-owned status update and missed-event recovery without replay.
  - **Files / area:** E2E tests/network instrumentation/test-only state driver; S5 evidence.
  - **Requirements:** REQ-SSE-001..004; REQ-PROJECT-010/011/016.
  - **Acceptance:** AC-SSE-001..004, AC-PROJECT-011/016.
  - **Implementation constraints:** Authoritative transition goes through the state service; no direct test DB update; final E2E uses real browser SSE/FastAPI/PostgreSQL, not the controlled fake transport. Network trace must show SSE connect and `STREAM_READY` before the handshake Snapshot on initial load and reconnect.
  - **Verification:** Journey 3: create → connect → ready → Snapshot → backend named command → PostgreSQL NOTIFY → Snapshot refresh → correct status/version. Journey 4: disconnect → backend change → reconnect → ready/buffer → Snapshot/reconcile → correct state without replay. Assert multiple real heartbeats do not change database/UI Project version.
  - **Done condition:** Playwright/network traces plus API/DB assertions demonstrate the full handshake, heartbeat/control version semantics, stale/duplicate immunity, live update, and reconnect correctness.

## C001-S6

### Foundation Acceptance & Traceability

- [ ] 6.1 Run the complete clean-checkout regression and retain reproducible evidence.
  - **Objective:** Execute all S1–S5 static, unit, PostgreSQL integration/contract, and four Playwright journeys from an isolated clean environment.
  - **Files / area:** Evidence index and generated reports only; no new business feature.
  - **Requirements:** All direct CHANGE-001 Requirements listed in proposal plus REQ-ARCH-001 Foundation boundary, REQ-PROJECT-018 partial, and REQ-GOVERNANCE-010/015 gates.
  - **Acceptance:** AC-FOUNDATION-001, AC-DATA-001, AC-PROJECT-010/011/013/014/016/017, AC-SSE-001..004, AC-ARCH-001 Foundation scope, AC-GOVERNANCE-010/014/015; AC-PROJECT-018 partial evidence only.
  - **Implementation constraints:** No failure waiver, threshold reduction, deleted test, SQLite substitution, or mock-as-E2E; record non-PASS honestly.
  - **Verification:** Run documented one-by-one commands with environment/tool versions, timestamps, exit codes, reports, traces, logs, schema catalog, and relevant hashes.
  - **Done condition:** Evidence index resolves every fully executable AC to an executed artifact or explicit non-PASS result; AC-PROJECT-018 remains `UNIMPLEMENTED` with C001 partial evidence and C003 completion boundary.

- [ ] 6.2 Run the Change scope, architecture, migration, and red-line applicability audits.
  - **Objective:** Prove absence of future capabilities and prohibited dependencies/routes/tables, audit REQ-ARCH-001 frontend import/bundle ownership, confirm one process-group topology, and verify every schema diff maps to Alembic.
  - **Files / area:** Route/dependency/schema/module inventories and S6 audit report only.
  - **Requirements:** REQ-ARCH-001; REQ-PROJECT-004..007; REQ-SCOPE-001..019; REQ-EVIDENCE-010; REQ-GOVERNANCE-005/006/011; REQ-UI-012/015.
  - **Acceptance:** AC-ARCH-001 Foundation-scope STATIC audit plus corresponding scope/governance ACs; future/global parts and red-line items recorded applicable/not-yet-applicable without false PASS.
  - **Implementation constraints:** Scope Guards are Change gates, not Slice business outcomes; no OPEN/PROPOSED decision becomes USER_CONFIRMED.
  - **Verification:** Compare Git diff, frontend dependency/import/bundle graph, secret scan, dependency locks, runtime topology, OpenAPI/routes, migrations/catalog, event schemas, worker registry, and UI navigation against AC-ARCH-001, proposal Out of Scope, and all 15 red lines.
  - **Done condition:** Foundation frontend contains no crawler process core, LLM judgment, clustering, scoring, backend runtime package, or secret; audit reports zero future leakage or blocking failure; no future/global requirement or non-applicable red line is marked PASS.

- [ ] 6.3 Reconcile Requirement → AC → capability/scenario → Slice/task → planned/executed verification coverage.
  - **Objective:** Update quality traceability only from actual artifacts/evidence and produce machine-checkable orphan/invalid-reference counts.
  - **Files / area:** `docs/quality/TRACEABILITY.md`, coverage report, quality checker if a non-destructive extension is needed.
  - **Requirements:** Direct CHANGE-001 Requirements, documented partial cross-Change Requirements, REQ-GOVERNANCE-015.
  - **Acceptance:** All fully executable direct ACs; AC-PROJECT-018 and other cross-Change ACs remain `PARTIAL COVERAGE / FUTURE COMPLETION` and `UNIMPLEMENTED`; AC-ARCH-001 has Foundation-scope evidence without global promotion.
  - **Implementation constraints:** Do not fabricate implementation path, result, test, or evidence; Result changes only from executed evidence; do not change Spec Baseline/Requirement/AC meaning.
  - **Verification:** Automated report asserts zero orphan Requirement, orphan AC, capability-without-Requirement, task-without-Acceptance, Acceptance-without-planned-verification, and invalid ID references.
  - **Done condition:** Coverage counts reconcile exactly and every partial Rollup/E2E row remains non-PASS.

- [ ] 6.4 Finalize Foundation runbook and CHANGE-001 completion report without adding functionality.
  - **Objective:** Document clean startup/migration/test commands, implemented file/database scope, results, incomplete/future items, and acceptance conclusion for independent review.
  - **Files / area:** README/developer runbook and CHANGE-001 evidence/completion report only.
  - **Requirements:** REQ-GOVERNANCE-015; REQ-FOUNDATION-001.
  - **Acceptance:** AC-GOVERNANCE-015, AC-FOUNDATION-001.
  - **Implementation constraints:** S6 may repair documentation/evidence wiring only; any missing behavior returns to its owning earlier Slice and cannot be smuggled into S6.
  - **Verification:** A reviewer follows the runbook on a clean checkout; completion checklist contains implementation scope, file changes, database changes, test results, incomplete items, and acceptance conclusion.
  - **Done condition:** Independent review can reproduce the Foundation and see every remaining future/partial item without ambiguity.
