# Spec Delta

## Purpose

定义 NeedRadar Foundation 可执行的本地 Web/API/PostgreSQL 产品边界、健康契约、可复现开发运行时及不越过后续 Change 的架构护栏。

## ADDED Requirements

### Requirement: Executable local product boundary
NeedRadar Foundation SHALL expose a locally runnable Web application and backend API, and SHALL use PostgreSQL rather than SQLite as the integration persistence system. Traceability: REQ-FOUNDATION-001, REQ-PROJECT-002 (partial), AC-FOUNDATION-001; C001-S1.

#### Scenario: Clean checkout starts the Foundation boundary
- **WHEN** a developer follows the documented clean-checkout setup with the pinned toolchains, locked dependencies, environment template, migrations, and local PostgreSQL
- **THEN** the Web and API start on documented localhost addresses and the Web can reach the API

#### Scenario: API reconnects after process restart
- **WHEN** the S1 API process is restarted while its PostgreSQL 18 database and empty Alembic baseline remain available
- **THEN** the new API process reconnects and can pass readiness without claiming Research Project persistence before the S2 table exists

#### Scenario: SQLite cannot satisfy integration acceptance
- **WHEN** Foundation integration or E2E acceptance is executed
- **THEN** the test target uses PostgreSQL and rejects SQLite as final evidence

### Requirement: Health and readiness are distinct
The backend SHALL provide liveness and readiness contracts that distinguish a running API process from its ability to use PostgreSQL. Traceability: REQ-FOUNDATION-001, AC-FOUNDATION-001; C001-S1.

#### Scenario: Healthy API process
- **WHEN** the API process is running and its liveness endpoint is requested
- **THEN** it returns a successful response without requiring a database query

#### Scenario: READY-001 database reachable and schema at head
- **WHEN** the readiness endpoint can execute a real lightweight PostgreSQL query and the database Alembic revision equals the application's current head
- **THEN** it returns a successful response identifying database connectivity and schema revision as ready

#### Scenario: READY-002 database unavailable
- **WHEN** the API process is running but the PostgreSQL probe fails
- **THEN** readiness returns HTTP 503 with a structured response and liveness remains independently observable

#### Scenario: READY-003 database schema behind
- **WHEN** PostgreSQL is reachable but its Alembic revision is behind the application's current head
- **THEN** readiness returns HTTP 503 without applying a migration

#### Scenario: READY-004 database schema revision unknown
- **WHEN** PostgreSQL is reachable but its Alembic revision is missing, divergent, or unknown to the application migration graph
- **THEN** readiness returns HTTP 503 without changing schema state

#### Scenario: READY-005 liveness is independent of database
- **WHEN** PostgreSQL is unavailable while the API process can still serve HTTP
- **THEN** `/health` remains successful and does not imply business readiness

### Requirement: Fixed runtime, database, and test contract
Foundation SHALL pin Node.js 24.x LTS, one repository-pinned pnpm version and `pnpm-lock.yaml`, Python 3.11.x through `.python-version`, uv through `pyproject.toml` and `uv.lock`, PostgreSQL 18.x at the latest supported minor in that major, and Psycopg 3 async as the sole PostgreSQL driver family. Backend tests SHALL use pytest and pytest-asyncio with `asyncio_mode = strict`; integration and E2E evidence MUST use an isolated real PostgreSQL database supplied through `TEST_DATABASE_URL`, never SQLite or a developer's ordinary database. Traceability: explicit CHANGE-001 Design Patch R1, REQ-FOUNDATION-001, REQ-ARCH-002/010 (`SHOULD` baseline retained); C001-S1/S6.

#### Scenario: Runtime manifests are authoritative
- **WHEN** a clean checkout resolves toolchains and dependencies
- **THEN** Node major 24, the pinned pnpm packageManager, Python 3.11.x, uv locks, PostgreSQL 18.x, and Psycopg 3 async resolve from repository declarations without global pip/npm state or competing lockfiles/drivers

#### Scenario: Async unit tests remain isolated
- **WHEN** the unit suite runs under pytest-asyncio strict mode
- **THEN** it uses no network, PostgreSQL, or developer `.env` by default and each async test owns its event-loop resources explicitly

#### Scenario: PostgreSQL tests use isolated lifecycle
- **WHEN** integration or E2E tests execute
- **THEN** `TEST_DATABASE_URL` identifies a validated dedicated test database or isolated test-database lifecycle, migrations prepare it deterministically, cleanup is order-independent, and SQLite cannot satisfy the evidence

#### Scenario: Migration mechanics are independently verified
- **WHEN** the S1 migration suite runs on a clean disposable PostgreSQL 18 database
- **THEN** it performs clean DB → `alembic upgrade head`, verifies the current revision, and exercises the Change-defined downgrade/re-upgrade strategy without application `create_all`

### Requirement: Localhost and secret boundary
Foundation SHALL bind Web and API to `127.0.0.1` by default, expose documented URLs `http://localhost:3000` and `http://localhost:8000`, allow only explicitly configured local Web origins in CORS, and keep all secrets in backend runtime configuration. It MUST NOT use wildcard CORS as the formal configuration or place secrets in `NEXT_PUBLIC_*`, client bundles, API/SSE payloads, browser storage, tracked `.env`, or structured logs. Traceability: explicit CHANGE-001 Design Patch R1, REQ-PROJECT-002 (partial), REQ-ARCH-001/011/012 (Foundation scope); C001-S1/S6.

#### Scenario: Default services are local-only
- **WHEN** the documented Foundation startup commands run with default development configuration
- **THEN** Web and API bind to `127.0.0.1`, are reachable at the documented localhost URLs, and do not listen on `0.0.0.0`

#### Scenario: CORS allows only explicit local Web origins
- **WHEN** browser-origin requests reach the API
- **THEN** `http://localhost:3000` is allowed, optional `http://127.0.0.1:3000` is allowed only when explicitly listed, and wildcard origins are absent

#### Scenario: Secrets cannot cross into the browser
- **WHEN** manifests, environment templates, generated bundles, API responses, SSE messages, browser storage, Git tracking, and structured logs are audited
- **THEN** `.env.example` contains placeholders only, real `.env` is ignored, and no backend secret appears in any client-visible or logged surface

### Requirement: Reproducible dependency and command contract
The Foundation SHALL document and lock the Python and Node dependencies, provide `.env.example`, and provide the canonical root entries `pnpm db:up`, `pnpm db:migrate`, `pnpm dev`, `pnpm check`, `pnpm test:unit`, `pnpm test:integration`, `pnpm test:migration`, and `pnpm test:e2e` after locked pnpm/uv installation. Traceability: explicit CHANGE-001 instruction, REQ-GOVERNANCE-010..011; C001-S1/S6.

#### Scenario: No implicit global project configuration
- **WHEN** a new supported checkout follows the documented commands
- **THEN** project dependencies and configuration resolve from repository files and declared prerequisites rather than undeclared machine-global packages or settings

#### Scenario: Schema authority is Alembic
- **WHEN** a clean database is prepared
- **THEN** Alembic migrations create the application schema and application startup does not use `create_all` as normal schema management

### Requirement: Preferred technology baseline retains its source strength
The Foundation SHALL preserve the baseline's `SHOULD` strength for framework choice: the implementation SHOULD use Next.js 15+, React 19+, TypeScript, Tailwind CSS, FastAPI, SQLAlchemy, Alembic, and PostgreSQL. The explicit CHANGE-001 runtime pins above are implementation policy for this Change, not a retroactive strengthening of the Spec Baseline. Equivalent framework deviation requires an explicit later design decision. Traceability: REQ-ARCH-002, REQ-ARCH-010; C001-S1.

#### Scenario: Foundation technology audit
- **WHEN** the implemented dependency manifests are audited
- **THEN** the preferred baseline is present or an explicit approved deviation is recorded without strengthening the source `SHOULD` into an unconditional requirement

### Requirement: Logical worker roles without microservices
The Foundation SHALL make `crawler_worker`, `analysis_worker`, and `clustering_worker` independently identifiable as logical task boundaries, while it MUST NOT implement their future business operations or require independent services. Traceability: REQ-ARCH-003 (partial), REQ-ARCH-013 (MAY), AC-ARCH-003 (partial); C001-S1.

#### Scenario: Worker boundary inventory
- **WHEN** the Foundation runtime/task registry is inspected
- **THEN** all three named roles have distinct interfaces or namespaces and may coexist in the backend process group

#### Scenario: No fake worker business
- **WHEN** the Foundation worker boundary is exercised
- **THEN** it creates no Crawl Job, Evidence, Model Run, Signal, Cluster, Score, Opportunity, Report, or evaluation output

### Requirement: Foundation frontend and backend responsibility boundary
The browser SHALL remain limited to Foundation pages, interaction, state display, API calls, and SSE display; it MUST NOT own crawler process control, semantic judgment, clustering, scoring, or authoritative Project state, all of which remain backend responsibilities in their owning Changes. Traceability: REQ-ARCH-001, REQ-ARCH-011/012 (partial), AC-ARCH-001, AC-ARCH-011/012 (partial); C001-S1/S4.

#### Scenario: Frontend dependency boundary audit
- **WHEN** Foundation frontend imports, bundles, routes, and data flows are inspected
- **THEN** no crawler process core, LLM judgment, clustering, scoring, backend domain/runtime package, secret, or authoritative Project mutation policy is imported into or executes in the browser bundle

#### Scenario: Backend ownership remains extensible
- **WHEN** Foundation module ownership is inspected
- **THEN** Project persistence/state/API/SSE have backend owners and future business responsibilities are neither client-owned nor falsely implemented

### Requirement: Structured backend logging foundation
Backend logs SHALL be structured with `timestamp`, nullable `project_id`, nullable `job_id`, `stage`, `level`, `message`, and `metadata`; Foundation activity SHALL use `job_id = null` rather than create a fake job. Traceability: REQ-RESILIENCE-007 (partial), REQ-RESILIENCE-008 (MAY), AC-RESILIENCE-007 (partial); C001-S1/S6.

#### Scenario: Project-scoped log record
- **WHEN** a Foundation Project operation emits a backend log
- **THEN** the record conforms to the structured fields, contains the real project identifier, and has a null job identifier

#### Scenario: Non-project log record
- **WHEN** startup, health, or readiness emits a backend log without Project context
- **THEN** project and job identifiers are null while the other required fields remain present

### Requirement: Foundation scope guard
The Foundation MUST NOT introduce account/login/membership/payment/multi-user/team features, SaaS/mobile delivery, automated outreach/marketing/publishing, second-level whole-web monitoring, Kafka, microservices, Elasticsearch, Neo4j, GraphRAG, self-hosted analysis models, multi-model routing, LLM product scoring, chat-only/single-table substitution, spinner-only long-task semantics, or any CHANGE-002–010/V0.2 business capability. Traceability: REQ-PROJECT-004..007, REQ-SCOPE-001..019, REQ-EVIDENCE-010, REQ-GOVERNANCE-005..006, REQ-UI-012/015; Change gate only.

#### Scenario: Static scope audit
- **WHEN** Foundation routes, migrations, dependencies, task registry, UI, and source ownership are inventoried
- **THEN** none of the prohibited or future capabilities is present and only the explicitly named logical worker boundaries exist
