# Design

## Context

See `proposal.md` for motivation and scope. The repository currently contains planning/quality documents only: no application source, dependency manifest, database schema, main OpenSpec capability, or prior Change exists. CHANGE-001 must therefore create a reproducible Foundation without treating the rest of V0.1 as implemented.

Controlling constraints are the Spec Baseline plus USER_CONFIRMED DEC-003/006/007/008 and the explicit current Design Patch R1 instruction. That current instruction refines DEC-008's unsafe literal Snapshot→Connect ordering to subscription-ready Connect/Buffer/Snapshot/Reconcile while preserving its meaning: PostgreSQL/backend REST remains truth, SSE remains lossy notification, and no replay store is introduced. Project state is backend-owned; ordinary delete is soft delete; schema changes use Alembic; tests cannot claim PostgreSQL integration from SQLite. The six Slice boundaries in `docs/quality/PLAN.md` remain unchanged. `DESIGN_BLOCKER`: none.

## Goals / Non-Goals

**Goals:**

- Fix enough architecture and contracts that C001-S1 can begin without making product or data-model choices during scaffolding.
- Provide one process-group architecture with clean Web, API, persistence, event, and future worker ownership boundaries.
- Make a clean checkout, schema migration, static checks, unit tests, real PostgreSQL integration, and Playwright E2E reproducible.
- Make every direct CHANGE-001 Requirement traceable to scenarios, Slice tasks, and a named verification target.

**Non-Goals:**

- No Planner, Terra, Prompt, Model Run, crawler execution/job/attempt, source/evidence, signal, embedding, cluster, score, opportunity, report/export, Gold Set/evaluation, or V0.2 implementation.
- No independently deployed worker service, queue product, durable event store, event sourcing, or historical SSE replay.
- No complete satisfaction claim for any cross-Change Rollup/E2E Requirement.

## Decisions

### D-001 Repository structure: one monorepo, two applications, no shared-package layer yet

Planned Foundation tree:

```text
NeedRadar/
├── apps/
│   ├── web/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   └── research/{new,[projectId]}/
│   │   ├── src/{components,lib}/
│   │   └── tests/
│   └── api/
│       ├── src/needradar/
│       │   ├── api/
│       │   ├── core/
│       │   ├── db/
│       │   ├── projects/
│       │   └── workers/
│       ├── migrations/{env.py,versions/}
│       └── tests/{unit,integration}/
├── tests/e2e/
├── docs/
├── openspec/
├── compose.yaml
├── package.json
├── pnpm-workspace.yaml
├── pnpm-lock.yaml
├── pyproject.toml
├── uv.lock
├── .nvmrc
├── .node-version
├── .python-version
└── .env.example
```

`apps/api` is one modular FastAPI application, not a service collection. Python domain/application code lives under one import root; `projects` owns the aggregate and state service, `db` owns SQLAlchemy/Alembic wiring, and `workers` owns only logical role contracts. `apps/web` is the only browser application. A `packages/` directory is deliberately omitted until a real cross-app package exists; generated OpenAPI TypeScript types stay in `apps/web/src/lib/api/generated`.

Alternative considered: separate API/worker microservices and a generic shared package. Rejected because it violates the V0.1 simplicity/scope guard and creates deployment/ownership abstractions before business consumers exist.

### D-002 Runtime and dependency reproducibility

- Node.js is pinned to `24.x` LTS. Both `.nvmrc` and `.node-version` declare major 24, `package.json.engines.node` enforces it, root `packageManager` pins an exact pnpm release, and `pnpm-lock.yaml` is the sole JavaScript lock authority. npm/yarn locks and automatic adoption of Node 26 Current are rejected.
- Python is pinned to CPython `3.11.x` in `.python-version`. `uv` owns the root `pyproject.toml` and committed `uv.lock`; system/global pip state is never part of the runtime. The local Python 3.14.6 installation is explicitly not the project contract. Python 3.11 is chosen to reduce CHANGE-003 MediaCrawler integration risk, not because the Spec Baseline mandates a Python minor.
- PostgreSQL development and formal test baseline is `18.x`, using the latest supported minor within major 18 and an official image pinned to an explicit patch/image digest during S1. PostgreSQL 19 beta and SQLite are invalid acceptance targets.
- Psycopg 3 async is the sole PostgreSQL driver family. SQLAlchemy async uses the correct `postgresql+psycopg://...` configuration; Alembic uses the same family. `asyncpg`, `psycopg2`, and competing formal drivers are absent.
- Backend tests use pytest and pytest-asyncio with `asyncio_mode = strict`. Unit tests default to no network/database and do not read a developer `.env`; integration tests require `TEST_DATABASE_URL` for an isolated real PostgreSQL database; Playwright drives the real Web → API → PostgreSQL stack.
- `.env.example` contains placeholder values only for `DATABASE_URL`, `TEST_DATABASE_URL`/validated test-admin lifecycle, explicit Web origins, server/public API locations, log level, and SSE heartbeat interval; documented defaults live in the runbook rather than embedding any real secret. Real `.env` is Git-ignored.
- Default bind hosts are `127.0.0.1`; documented URLs are `http://localhost:3000` and `http://localhost:8000`. CORS explicitly allows `http://localhost:3000` and may list `http://127.0.0.1:3000`; wildcard origin is forbidden.
- Secrets enter backend runtime only. They are forbidden from `NEXT_PUBLIC_*`, generated/client bundles, API/SSE payloads, browser localStorage, Git-tracked `.env`, and structured logs.
- Canonical root command surface is fixed as: `corepack enable`; `pnpm install --frozen-lockfile`; `uv sync --frozen --python 3.11`; `pnpm db:up`; `pnpm db:migrate` (explicit Alembic upgrade); `pnpm dev`; `pnpm check`; `pnpm test:unit`; `pnpm test:integration`; `pnpm test:migration`; and `pnpm test:e2e`. Root scripts may delegate to app-local commands but MUST preserve these documented entry points, use repository-local tools, and expose non-zero failures. No undeclared globally installed library or setting is assumed.

Alternative considered: run the whole developer loop only inside Docker. Rejected as the sole path because local Next.js/Python iteration is simpler on the target Mac; Docker remains the deterministic PostgreSQL boundary. A containerized full-stack clean-run may be added as convenience, not as a second production topology.

### D-003 Frontend architecture and routes

- Framework baseline: Next.js 15+ App Router, React 19+, strict TypeScript, Tailwind CSS.
- Routes in this Change: `/` redirects to `/dashboard`; `/dashboard`; `/research/new`; `/research/[projectId]`. Future Plan/Crawl/Demand/Evidence/Opportunity/Report routes are not scaffolded as fake screens.
- Server Components may perform non-live list reads. A Project view that enables live status uses a Client Component to own the complete SSE handshake; it MUST NOT hydrate a pre-fetched Project Snapshot as the live handshake baseline because subscription readiness must precede that Snapshot.
- A single typed API layer owns base URL, Problem Details parsing, time parsing, and generated OpenAPI types. Runtime SSE envelope validation uses a small schema validator; components do not issue ad hoc fetches.
- State uses server-rendered data plus a local reducer keyed by Project ID/version. No Redux/Zustand or other application-wide state framework is introduced. The router refreshes server data after successful mutations.
- The live client opens SSE, waits for `STREAM_READY`, begins buffering mutation events, fetches the authoritative Project Snapshot, discards buffered versions `<=` Snapshot version, reconciles newer versions in order, then enters live mode. On disconnect or handshake failure it closes/discards the incomplete connection and buffer and repeats the complete handshake with bounded exponential backoff. Event payloads notify; they do not directly replace Project facts.
- Dashboard cards display only Foundation facts. Demand Cluster/Evidence/Top Demand/platform coverage remain hidden or explicitly unavailable, never numeric `0`.

Alternative considered: browser-local cache/localStorage as the Project store. Rejected because it conflicts with backend-owned truth. A large client state/query framework is also rejected until Foundation complexity justifies it.

### D-004 Backend architecture and ownership

FastAPI exposes thin routers; application services own transactions and policy; repositories own queries but never commit or mutate status arbitrarily; SQLAlchemy models map persistence. Dependencies are injected per request. The app lifecycle creates/disposes one async SQLAlchemy engine and session factory; each request obtains a short-lived `AsyncSession`.

The transaction boundary is the application service:

1. Validate command and expected version.
2. Load/update through the repository inside one transaction.
3. Apply the state/delete policy and increment `project_version`.
4. Queue PostgreSQL notification in the same transaction.
5. Commit once; only then can PostgreSQL deliver the notification.

Repositories may `flush` but never `commit`. API schemas reject unknown fields. The browser cannot write database/domain objects directly.

### D-005 Health, readiness, configuration, and API error format

- `GET /health`: liveness only, HTTP 200 `{status:"ok", service, version}` while the process can serve; no database query.
- `GET /ready`: first executes a lightweight real PostgreSQL probe such as `SELECT 1`, then reads the database Alembic revision and compares it with the application's exact current `head`. Success requires both checks and returns HTTP 200 with `database:"ok"` and `schema:"head"`.
- Database unavailable returns HTTP 503 with `database:"unavailable"`. Reachable database with a missing, behind, divergent, or unknown revision returns HTTP 503 with a non-secret `schema` reason. `/health` remains successful whenever the API process can serve, including during either readiness failure.
- Startup validates configuration but does not run migrations or call `metadata.create_all`. `/ready` is read-only and never performs or repairs migrations; schema changes require the explicit documented Alembic command.
- READY-001 covers DB available + schema=head; READY-002 DB unavailable; READY-003 schema behind; READY-004 missing/divergent/unknown revision; READY-005 health stays process-alive while DB is unavailable.
- Errors use `application/problem+json` compatible with RFC 9457: `type`, `title`, `status`, `detail`, `code`, `request_id`, optional `field_errors`, and optional `current_project_version`.

Status policy:

| Condition | HTTP | Code |
|---|---:|---|
| Request/schema validation | 422 | `VALIDATION_ERROR` |
| Missing optimistic precondition | 428 | `PRECONDITION_REQUIRED` |
| Unknown or soft-deleted Project | 404 | `PROJECT_NOT_FOUND` |
| Illegal state command | 409 | `ILLEGAL_PROJECT_TRANSITION` |
| Stale expected version | 409 | `PROJECT_VERSION_CONFLICT` |
| Readiness dependency unavailable | 503 | `SERVICE_NOT_READY` |
| Readiness schema not at exact head | 503 | `SCHEMA_NOT_READY` |

### D-006 PostgreSQL and migration foundation

- `research_project.id` is application-generated UUIDv4 stored as native PostgreSQL `uuid`; this avoids a database extension solely for IDs and permits IDs before flush/event construction.
- All lifecycle columns use `timestamptz`; persistence and service clocks normalize to UTC; JSON uses RFC 3339 with `Z`/explicit UTC offset.
- Alembic is schema authority. C001-S1 creates the environment and an empty baseline revision so upgrade/downgrade mechanics can be tested without a Research business table. C001-S2 adds the `research_project` migration.
- SQLAlchemy async, application queries, notification listener, and Alembic use the Psycopg 3 driver family; no second PostgreSQL driver is introduced. Connection pooling uses conservative local defaults, pre-ping, and explicit dispose on shutdown. Long-lived SSE subscriptions use a dedicated Psycopg 3 async notification connection rather than holding an ORM transaction/session open.
- Integration tests receive `TEST_DATABASE_URL` for a validated dedicated PostgreSQL 18 instance/database. A session lifecycle may create a uniquely named database from a separately declared admin URL, runs `alembic upgrade head`, executes order-independent tests with transactions or deterministic cleanup, terminates remaining connections, and drops only that validated test database. E2E uses its own isolated database/container and migrations; no test points at the developer's ordinary database.
- Restart persistence is verified by creating data through API process A, stopping it, starting process B against the same database, and reading the data. Transaction rollback fixtures are not used as the only evidence for cross-process behavior.

Alternative considered: SQLite for tests. Rejected by the acceptance contract. PostgreSQL schemas inside one database were considered, but separate test databases better exercise extensions/catalog/migration isolation and avoid search-path leakage.

### D-007 Foundation Research Project schema

`research_project` is the only CHANGE-001 business table:

| Column | PostgreSQL shape | Foundation semantics |
|---|---|---|
| `id` | `uuid` PK | Application UUIDv4 |
| `name` | `varchar(200)` NOT NULL | Trimmed, non-empty |
| `original_query` | `text` NOT NULL | Trimmed, non-empty |
| `context` | `text` NULL | Optional user context |
| `status` | `varchar(32)` NOT NULL + CHECK | Exact 13-value DEC-006 vocabulary |
| `planner_version` | `varchar(64)` NULL | Reserved baseline field; remains null in Foundation |
| `project_version` | `bigint` NOT NULL DEFAULT 1 + CHECK `>=1` | Optimistic/notification version |
| `failed_from_status` | `varchar(32)` NULL + CHECK | Non-null only while FAILED; only retryable source values |
| `created_at` | `timestamptz` NOT NULL | Server UTC |
| `updated_at` | `timestamptz` NOT NULL | Updated on committed observable mutation |
| `completed_at` | `timestamptz` NULL | Set only on first transition to READY |
| `deleted_at` | `timestamptz` NULL | Ordinary soft delete marker |

Database checks enforce status vocabulary, version positivity, FAILED/failure-source consistency, and READY/completed-at consistency. Indexes are limited to Foundation query paths: the primary key, `(deleted_at, updated_at DESC, id)`, and `status` for lifecycle queries. Future tables/fields/indexes arrive through later migrations.

No JSON metadata or error-summary column is added: CHANGE-001 has no domain need that structured logs and `failed_from_status` do not cover. No Crawl Job, source, Evidence, Signal, Cluster, Snapshot, Opportunity, Report, Model Run, Gold Set, or event-store table is created.

### D-008 Project REST and Snapshot contract

Concrete routes use `/api/projects` (allowed equivalent to baseline suggestions):

| Method/path | Input | Success | Notes |
|---|---|---|---|
| `POST /api/projects` | `{name, original_query, context?}` | 201 Project Snapshot; `Location` | Server owns all lifecycle fields; emits `PROJECT_CREATED` v1. |
| `GET /api/projects` | none | 200 active Project summaries | Filters `deleted_at IS NULL`; deterministic `updated_at DESC,id` order. |
| `GET /api/projects/{id}` | UUID | 200 Project Snapshot | Deleted and unknown both 404. |
| `DELETE /api/projects/{id}` | `If-Match: "<project_version>"` | 204 | Sets `deleted_at`, preserves status, increments version, emits `PROJECT_DELETED`; never purges. |
| `GET /api/projects/{id}/events` | SSE accept | 200 stream | Active Project only. |

The Snapshot shape contains Project fields and derived Foundation progress only:

```json
{
  "project": {"id": "...", "name": "...", "original_query": "...", "context": null, "status": "DRAFT", "planner_version": null, "created_at": "...Z", "updated_at": "...Z", "completed_at": null},
  "project_version": 1,
  "progress": {"stage": "DRAFT", "terminal": false, "updated_at": "...Z"}
}
```

No fabricated count or percentage is persisted or returned. `If-Match` is required for DELETE. Application/internal state commands also require `expected_project_version`; no production endpoint accepts arbitrary target state. C001-S3 exposes the state service through an application command port for future Changes. The Playwright environment may mount a test-only driver router that invokes the same service, is absent from production OpenAPI/builds, and never writes the repository directly; this allows SSE journeys to cause authoritative transitions without implementing Planner/Crawl UI.

### D-009 Formal Project transition policy and independent test oracle

Production owns a data-defined transition table used only by the state service. Tests MUST NOT import, call, reflect, serialize, or derive expectations from that production definition. The test suite separately owns explicit `EXPECTED_ALLOWED_TRANSITIONS` and `EXPECTED_FORBIDDEN_TRANSITIONS`, written manually from DEC-006, the `project-state` capability spec, and AC-PROJECT-016/017/AC-GOVERNANCE-014. It takes the Cartesian product of the 13 confirmed states, asks the independent oracle for each expected result, then invokes production behavior. An allowed pair still requires its named command and preconditions; all targets not listed by the independent oracle are expected forbidden. `fail` is valid only from five retryable stages. FAILED has one dynamic allowed target equal to its persisted `failed_from_status`.

| Source | Allowed target(s) | Command/action | Commit side effects | Failure behavior |
|---|---|---|---|---|
| DRAFT | PLANNING | `begin_planning` | Clear failure source; version +1; status event | Every other target/command rejects 409; no mutation/event |
| PLANNING | PLAN_READY | `mark_plan_ready` | Version +1; status event | Every other target/command rejects 409 |
| PLAN_READY | CRAWLING | `start_collection` | Version +1; status event; no Crawl Job is created here | Every other target/command rejects 409 |
| CRAWLING | PAUSED | `pause_collection` | Version +1; status event; interface boundary only | Invalid command rejects/rolls back |
| CRAWLING | CRAWL_PARTIAL | `mark_crawl_partial` | Version +1; status event | Invalid command rejects/rolls back |
| CRAWLING | ANALYZING_SIGNALS | `begin_signal_analysis` | Version +1; status event; no analysis starts here | Invalid command rejects/rolls back |
| CRAWLING | FAILED | `fail` | Store `failed_from_status=CRAWLING`; version +1; status event | Missing failure context/expected version rejects |
| CRAWLING | CANCELLED | `cancel` or collection `stop` alias | Version +1; terminal status event; retain all data | Invalid/stale command rejects |
| PAUSED | CRAWLING | `resume_collection` | Version +1; status event; future Crawl jobs separately follow WAITING→RUNNING | No other target except CANCELLED |
| PAUSED | CANCELLED | `cancel` or `stop` | Version +1; terminal status event | All other targets reject |
| CRAWL_PARTIAL | CRAWLING | `retry_collection` | Version +1; status event; no attempt is created in Foundation | No other target except listed |
| CRAWL_PARTIAL | ANALYZING_SIGNALS | `continue_with_partial` | Version +1; status event | No downstream analysis starts in Foundation |
| CRAWL_PARTIAL | CANCELLED | `cancel` | Version +1; terminal status event | All other targets reject |
| ANALYZING_SIGNALS | CLUSTERING | `begin_clustering` | Version +1; status event | No clustering starts in Foundation |
| ANALYZING_SIGNALS | FAILED | `fail` | Save source; version +1; status event | Invalid/stale command rejects |
| ANALYZING_SIGNALS | CANCELLED | `cancel` | Version +1; terminal status event | Other targets reject |
| CLUSTERING | CURATING_CLUSTERS | `begin_cluster_curation` | Version +1; status event | No curator starts in Foundation |
| CLUSTERING | FAILED | `fail` | Save source; version +1; status event | Invalid/stale command rejects |
| CLUSTERING | CANCELLED | `cancel` | Version +1; terminal status event | Other targets reject |
| CURATING_CLUSTERS | SCORING | `begin_scoring` | Version +1; status event | No scoring starts in Foundation |
| CURATING_CLUSTERS | FAILED | `fail` | Save source; version +1; status event | Invalid/stale command rejects |
| CURATING_CLUSTERS | CANCELLED | `cancel` | Version +1; terminal status event | Other targets reject |
| SCORING | READY | `complete` | Set `completed_at`; version +1; status event | Invalid/stale command rejects |
| SCORING | FAILED | `fail` | Save source; version +1; status event | Invalid/stale command rejects |
| SCORING | CANCELLED | `cancel` | Version +1; terminal status event | Other targets reject |
| READY | none | none | none | All state commands reject 409; delete remains separate |
| FAILED | exactly persisted retryable `failed_from_status` | `retry` | Clear failure source; version +1; status event | Null/invalid/client-selected source rejects 409 |
| CANCELLED | none | none | none | All state commands reject 409; delete remains separate |

Retryable failure sources are exactly `CRAWLING`, `ANALYZING_SIGNALS`, `CLUSTERING`, `CURATING_CLUSTERS`, and `SCORING`, matching DEC-006's explicit FAILED edges. The matrix contains 30 context-valid source/target pairs (including the five possible FAILED retry targets) and 139 forbidden pairs. Same-state requests are not observable transitions and do not increment versions.

Additional independent cases cover all five `FAILED + failed_from_status` retries, null/invalid failure sources, client arbitrary-target rejection, same-state/no-op, repeated commands, optimistic-version replay, deleted-Project rejection, READY/CANCELLED terminal behavior, and the absence of mutation/version/event side effects on every rejected case. Transition implementation and tests remain Foundation policy only. Future Changes invoke commands after their own work reaches the required boundary; this Change does not simulate that work.

### D-010 Project version and optimistic concurrency

`project_version` is a `bigint` that represents only Project Observable Mutation Version. Creation commits initial version 1; each later committed user-visible Foundation field change, state change, Foundation progress change, or soft delete increments it exactly once. It is not a timestamp or transport sequence and does not increment for reads, `STREAM_READY`, heartbeat, rejected/repeated/no-op commands, validation failures, or rolled-back transactions.

Mutation uses compare-and-swap against the expected version. The emitted domain notification uses the resulting committed database version and is queued inside the transaction; it never precomputes an uncommitted version or advances an event-local counter. PostgreSQL releases the notification only after commit. Concurrent writers using N yield at most one N+1 commit; losers receive 409 and the current version. Transport `event_id` is unique per SSE message but is never substituted for `project_version`.

### D-011 SSE implementation: PostgreSQL notification bus, no event store

PostgreSQL `LISTEN/NOTIFY` is the lightweight cross-process notification bus. A transaction calls `pg_notify` with a compact envelope; PostgreSQL releases the notification on commit. This supports later same-database worker processes without Kafka/Redis and does not create durable history.

Mutation-event wire format:

```text
id: <event_id UUID>
event: PROJECT_STATUS_CHANGED
data: {"event_id":"...","project_id":"...","project_version":2,"event_type":"PROJECT_STATUS_CHANGED","occurred_at":"...Z","payload":{"changed_fields":["status"]}}

```

Foundation mutation event types are exactly `PROJECT_CREATED`, `PROJECT_UPDATED`, `PROJECT_STATUS_CHANGED`, and `PROJECT_DELETED`. A mutation envelope has `event_id`, `project_id`, committed integer `project_version`, `event_type`, UTC `occurred_at`, and object `payload`; domain payload stays small and non-authoritative.

`STREAM_READY` and `HEARTBEAT` are control/transport events, not Project mutations. They have transport `event_id`, `project_id`, `connection_id`, `observed_project_version`, and time; `STREAM_READY` is emitted only after the server has established that Project subscription. Neither has a mutation `project_version` field and neither changes the database/UI Project version. Repeated heartbeats may carry the same `observed_project_version`, which is correct. The default heartbeat interval is 15 seconds and remains environment-configurable.

The API owns a dedicated async PostgreSQL listener and fans out to bounded per-connection queues. If a queue overflows, the server closes that stream so the client must Snapshot-recover; it never accumulates unbounded memory. Subscriber registration/removal occurs in `try/finally`; shutdown closes listeners and queues. The single Foundation browser stream is Project-specific, validates an active Project before headers, and after `PROJECT_DELETED` forwards that committed event then closes. Dashboard create/delete actions refresh the authoritative list; a multiplexed cross-Project stream is deferred because its heartbeat cannot satisfy DEC-008's non-fake `project_id` envelope on an empty Dashboard.

Initial and reconnect client algorithm:

1. Open a new Project SSE connection with a new handshake buffer.
2. Wait for a valid `STREAM_READY`; before it arrives, do not treat the stream as live-ready.
3. Once ready is observed, buffer every subsequent Project mutation event for that connection.
4. GET the authoritative Project Snapshot and apply it.
5. Discard buffered mutation events with `project_version <= snapshot.project_version`.
6. Order remaining buffered mutation notifications by `project_version`; use them to trigger authoritative Snapshot reconciliation until no buffered version exceeds current state.
7. Enter live mode. Ignore mutation events with `project_version <= currentVersion`; for a greater version, re-fetch Snapshot and adopt only a non-older response. Heartbeat updates connection health only.
8. On malformed/unknown message, retain current state and schedule bounded Snapshot recovery.
9. On disconnect at any phase, close/discard that connection and buffer, then repeat steps 1–8 with capped exponential backoff.

This ordering closes the old Snapshot → Connect gap: a mutation during Snapshot fetch or response processing is captured by the already-ready subscription buffer. No historical replay is needed.

The handshake state machine has an injectable transport/synchronization seam for deterministic client/contract tests. Tests use barriers or controlled transport callbacks—never sleep-and-hope timing—to prove:

- RACE-001 mutation before `STREAM_READY`: the later Snapshot reaches the committed latest version.
- RACE-002 mutation after `STREAM_READY` but before Snapshot request: event is buffered and final state is latest.
- RACE-003 mutation while Snapshot query is blocked: buffer retains it and reconciliation reaches latest.
- RACE-004 mutation after Snapshot response but before buffer drain: same handshake retains and reconciles it.
- RACE-005 disconnect during handshake: partial buffer is abandoned and a fresh full handshake succeeds.
- RACE-006 duplicate mutation event: observable mutation is not re-applied.
- RACE-007 mutation event at or below current version: current state cannot regress or re-apply.

The controlled transport is acceptable only for deterministic unit/contract coverage. C001-S5 Playwright still uses real browser SSE, FastAPI, PostgreSQL LISTEN/NOTIFY, and real Snapshot endpoints.

`Last-Event-ID` is neither required nor used for replay. Event IDs aid logging/deduplication only. Correctness follows from committed version + Snapshot.

Alternative considered: database event table/outbox with replay. Rejected because DEC-008 explicitly does not require a durable event store or historical replay. An in-process-only pub/sub was rejected because it would lose notifications across future same-database worker processes even within one process group.

### D-012 Logical worker boundary

`apps/api/src/needradar/workers` declares three role identifiers, role-specific task namespaces, and a dispatcher/handler protocol. Foundation registers the roles as unavailable/no-handler until their owning Change. It does not start idle daemons, create fake jobs, or expose success for unsupported work. Later Changes may attach in-process/background or separately scheduled handlers without moving domain ownership out of the backend.

This satisfies the logical-boundary contribution to REQ-ARCH-003 while leaving AC-ARCH-003 `PARTIAL COVERAGE / FUTURE COMPLETION` until real roles are independently identifiable/configurable in their accepting Changes.

### D-013 Structured logging

Use Python standard logging with a JSON formatter and `contextvars` for `request_id`, `project_id`, `job_id`, and `stage`. Every record serializes:

```text
timestamp, project_id, job_id, stage, level, message, metadata
```

`timestamp` is UTC; `metadata` is an object; secrets, connection strings, request bodies containing user context, and stack traces are not included in ordinary production messages. Foundation Project operations set the real `project_id` and `job_id=null`. Health/startup uses both IDs null. Request ID is retained as an additional correlation field. No fake Crawl Job is created to populate logs.

### D-014 Static, unit, integration, contract, and E2E strategy

The canonical root command spellings are fixed in D-002. C001-S1 may only choose their app-local delegated implementation details without renaming the documented entry points or changing the verification targets below.

| Slice | STATIC | UNIT | PostgreSQL INTEGRATION / CONTRACT | Playwright E2E | Exit evidence |
|---|---|---|---|---|---|
| C001-S1 | Node 24/pnpm-single-lock, Python 3.11/uv-single-lock, Psycopg-only, localhost/CORS/secret and frontend import/bundle audits; Web/Python static checks; OpenAPI diff; OpenSpec strict validate | Config parsing, pytest-asyncio strict isolation, error schema, worker registry, JSON log shape | PostgreSQL 18 empty baseline up/down/up; READY-001..005 for DB + exact Alembic head; no business restart test | Browser loads real Dashboard shell through localhost Web→API with no client secret | Clean-start/runtime/version log, readiness matrix, architecture report; AC-FOUNDATION-001 and Foundation-scope AC-ARCH-001 |
| C001-S2 | Migration/schema ownership check; generated client typecheck | Project validation, UTC serialization, soft-delete query policy, version CAS | Fresh migration/catalog checks; create/get/list; invalid payload; soft delete/default filtering; two API lifetimes against same DB; downgrade/upgrade | Journey 1 create→Dashboard row/status; Journey 2 create→delete→absent | AC-DATA-001/PROJECT-013 artifacts; AC-PROJECT-018 partial Project-only evidence, never full PASS |
| C001-S3 | No unrestricted repository status setter; frontend cannot import state policy; oracle/production dependency separation | Independent explicit expected 13×13 matrix, command preconditions, same-state/repeated/deleted, failure/retry, terminal states, version success/rollback/concurrency | Persist every status; failed source/clear; CAS conflict; post-commit notification/no rollback notification | Backend test driver changes state; UI renders backend status | AC-PROJECT-010/016/017 and AC-GOVERNANCE-014 reports |
| C001-S4 | Route/API ownership and no fixture/localStorage business-source audit | Dashboard reducer/version logic and unavailable-metric rendering | Dashboard list/snapshot queries use PostgreSQL; deleted returns 404 | Journey 1 and 2 plus conflicting local guess follows backend; real Web→API→PostgreSQL only | AC-PROJECT-011/014; AC-UI-002 explicitly partial |
| C001-S5 | Mutation/control schemas exclude future types; SSE endpoint/OpenAPI contract checks | Handshake reducer, version semantics, heartbeat/control non-mutation, RACE-001..007 with deterministic barriers/controlled transport, bounded backoff | LISTEN/NOTIFY commit/rollback/order; `STREAM_READY`; listener cleanup; not-found/deleted stream; queue overflow recovery | Journey 3 state command→real SSE→UI; Journey 4 disconnect→complete handshake→correct state | AC-SSE-001..004 contract/network traces |
| C001-S6 | Full scope/dependency/route/migration/traceability/red-line and REQ-ARCH-001 import/bundle audits | Full prior unit regression | Fresh isolated PostgreSQL 18 migrate and full integration/contract suite; S2 API restart | All four journeys from clean checkout | Retained evidence index; no new feature; AC-PROJECT-018 remains partial/UNIMPLEMENTED |

OpenAPI/schema checking consists of generating the FastAPI schema, validating it, comparing a committed snapshot, and regenerating/typechecking the Web client types. Mocks may cover client unit failures but never satisfy final Web→API→PostgreSQL E2E evidence.

### D-015 Acceptance evidence and traceability policy

Implementation will write evidence under a documented, reviewable location (for example `docs/quality/evidence/change-001/<slice>/`) with commands, environment/tool versions, timestamps, exit codes, reports/traces, and hashes where appropriate. C001-S6 updates result fields only from executed evidence. Until then every mapped row remains `UNIMPLEMENTED`, with implementation/test/evidence columns blank or planned.

Direct Requirement → capability → scenario → Slice mapping is maintained in the specs and tasks. Cross-Change items are labeled partial and cannot pass: AC-PROJECT-002/008/018, AC-UI-002, AC-ARCH-003/007/008/011/012, AC-API-007, and AC-RESILIENCE-007. AC-PROJECT-018 receives only Project soft-delete/exclusion evidence in C001; its shared-Source PostgreSQL clauses remain `UNIMPLEMENTED` until C003. AC-ARCH-001 receives Foundation-scope STATIC evidence while the global multi-Change Requirement remains `UNIMPLEMENTED`. Complete V0.1/E2E/rollup gates remain untouched.

## Slice Inputs, Outputs, and Exit Gates

| Slice | Input | Output | Exit Gate |
|---|---|---|---|
| C001-S1 | Approved CHANGE-001 design; empty application repo | Fixed Node 24/pnpm, Python 3.11/uv, Psycopg 3/PostgreSQL 18 localhost-safe Web/API/DB boundary; DB+head readiness; Alembic/test/logical-worker/frontend-architecture harness | Clean environment starts all three boundaries; READY-001..005 and baseline migration pass; secret/import audit passes; no Research business table or business restart claim |
| C001-S2 | S1 runtime and migration mechanism | Minimal Project migration/model/repository/service/CRUD/Snapshot, soft delete, and Project restart persistence | Real PostgreSQL schema/CRUD/two-process restart/delete tests pass; no future tables; AC-PROJECT-008 and full AC-PROJECT-018 remain partial/UNIMPLEMENTED |
| C001-S3 | S2 aggregate/version column; DEC-003/006 | Central command policy, independent test oracle, full state matrix, failure recovery, concurrency/event mutation seam | All 169 pairs against independent expectations plus repeat/deleted/terminal negatives pass; persisted version/failure rules pass |
| C001-S4 | S2/S3 API contracts | Real Dashboard create/list/get/delete/detail journey | Playwright proves Web→API→PostgreSQL; no fake metrics, local facts, or deleted cards |
| C001-S5 | S3 versioned mutations; S4 live UI | Subscription-ready Connect/Buffer/Snapshot/Reconcile + PostgreSQL-notify SSE lifecycle | RACE-001..007 and real-SSE Journeys 3/4 prove no handoff gap, non-mutating heartbeat/control, duplicate/stale immunity, cleanup, and recovery |
| C001-S6 | S1–S5 implemented outcomes | Clean-run evidence, regression, traceability/result review, architecture/scope/red-line audit, runbook | Every fully executable CHANGE-001 AC has retained evidence or honest non-PASS; AC-PROJECT-018 stays partial/UNIMPLEMENTED; no future/rollup promotion |

## Migration Plan

1. C001-S1 adds the Alembic environment and an empty Foundation baseline revision; verify upgrade/downgrade/up against a disposable PostgreSQL database.
2. C001-S2 adds one revision creating `research_project`, checks, and indexes; application startup requires the schema at head but never creates it automatically.
3. Test downgrade drops only the Foundation table/indexes/checks created by that revision, then re-upgrade verifies reproducibility. Local rollback before data matters is `alembic downgrade <baseline>`; after real local data exists, backup/export is required before downgrade.
4. No later Slice adds a business table in CHANGE-001. A necessary schema change must be a new Alembic revision, never an edited applied revision or manual SQL workflow.

## Risks / Trade-offs

- [PostgreSQL NOTIFY is lossy and payload-limited] → Keep payload compact/non-authoritative; bounded queues close on overflow; every initial/reconnect path GETs Snapshot.
- [A transient mutation can occur during initial/reconnect Snapshot handoff] → Establish subscription first, require `STREAM_READY`, buffer during Snapshot, reconcile by committed Project version, and cover all seven orderings deterministically.
- [No durable event history limits debugging/replay] → Structured logs and current database state are diagnostic sources; durable replay remains explicitly out of scope.
- [CPython 3.14 is installed locally but MediaCrawler compatibility is the larger future risk] → Pin project runtime to Python 3.11.x and change it only through a later explicit compatibility decision with locked full-suite evidence.
- [PostgreSQL-only tests cost more than SQLite] → Use isolated ephemeral databases and separate fast unit tests; never weaken integration evidence.
- [Status vocabulary precedes future behavior] → Keep all transition execution behind command ports, expose no future UI, and state clearly that a status transition policy is not the Planner/Crawl/Analysis implementation.
- [One Project-specific browser stream does not push cross-tab Dashboard changes] → Dashboard refreshes after its own mutations; CHANGE-001 live/reconnect acceptance runs on the Project view, and a future multiplexed contract requires its own valid heartbeat identity design.
- [Soft-deleted rows grow indefinitely] → Local Foundation scale is small; PURGE/retention remains a separately designed future maintenance capability.
- [Generated OpenAPI types can drift] → Commit schema snapshot/generated client and fail static checks on diff.

## Open Questions

None. Cosmetic Dashboard wording may be chosen during implementation without changing the specifications, architecture, Slice boundaries, or acceptance thresholds.
