# Spec Delta

## Purpose

定义空 Research Project aggregate 的最小 PostgreSQL 持久化、REST CRUD、soft delete、Snapshot 与结构化错误行为，为后续业务增量保留清晰边界。

## ADDED Requirements

### Requirement: Minimal Research Project persistence
The backend SHALL persist each Research Project in PostgreSQL with `id` as UUID primary key, `name`, `original_query`, nullable `context`, `status`, nullable `planner_version`, `created_at`, `updated_at`, nullable `completed_at`, nullable `deleted_at`, integer `project_version`, and nullable `failed_from_status`. It MUST NOT add future business tables or speculative metadata/error fields in CHANGE-001. Foundation SHALL add only indexes justified by these Project access paths. Traceability: REQ-DATA-001, REQ-ARCH-008 (partial), AC-DATA-001, AC-ARCH-008 (partial); C001-S2.

#### Scenario: Fresh migration creates the minimal schema
- **WHEN** Alembic upgrades a fresh PostgreSQL database to Foundation head
- **THEN** `research_project` contains exactly the Foundation-owned business fields and constraints required by this Change

#### Scenario: UTC temporal round trip
- **WHEN** a Project is created and reloaded
- **THEN** all persisted timestamps are timezone-aware UTC values and API serialization includes an explicit UTC offset

#### Scenario: Empty Project defaults
- **WHEN** a valid empty Project is created
- **THEN** it starts as `DRAFT` with `project_version = 1`, null planner/completion/deletion/failure fields, and server-owned timestamps

### Requirement: Create Project capability
The API SHALL create an empty Project from a non-empty `name`, non-empty `original_query`, and optional `context`; clients MUST NOT supply status, version, lifecycle timestamps, planner version, or failure source. The concrete `/api/projects` shape follows baseline REST guidance without making that suggested spelling mandatory for future capabilities. Traceability: REQ-PROJECT-013, REQ-ARCH-007 (partial), REQ-API-008 (`SHOULD`), AC-PROJECT-013, AC-ARCH-007 (partial); C001-S2.

#### Scenario: Valid Project creation
- **WHEN** a client submits valid name and original query with optional context
- **THEN** the API commits one Project and returns its authoritative representation

#### Scenario: Invalid creation payload
- **WHEN** a client omits required text, submits blank required text, includes an unknown forbidden domain field, or violates length/schema constraints
- **THEN** the API returns a structured HTTP 422 validation error and commits no Project

#### Scenario: Client attempts to select initial state
- **WHEN** a client includes `status`, `project_version`, or another backend-owned lifecycle field
- **THEN** validation rejects the request and no arbitrary state is persisted

### Requirement: List and get active Projects
The API SHALL list and get non-deleted Projects from PostgreSQL, and ordinary list/get MUST exclude soft-deleted rows. This is CHANGE-001 partial coverage of REQ/AC-PROJECT-018; full shared-Source retention remains UNIMPLEMENTED until CHANGE-003. Traceability: REQ-PROJECT-013, REQ-PROJECT-018 (partial), AC-PROJECT-013, AC-PROJECT-018 (partial); C001-S2.

#### Scenario: List active Projects
- **WHEN** active and soft-deleted Projects exist and the ordinary list capability is requested
- **THEN** only active Projects are returned in deterministic most-recently-updated order

#### Scenario: Get active Project
- **WHEN** an existing non-deleted Project identifier is requested
- **THEN** the API returns the persisted authoritative representation

#### Scenario: Missing or deleted Project
- **WHEN** an unknown or soft-deleted Project identifier is requested through ordinary get
- **THEN** the API returns the same structured HTTP 404 not-found contract without exposing deletion state

### Requirement: Ordinary Delete is soft delete
Ordinary Project DELETE SHALL atomically set `deleted_at`, update `updated_at`, and increment `project_version`; it MUST NOT physically remove the Project. CHANGE-001 MUST NOT create Source Content, Source Comment, Evidence, or Project-Source association tables and therefore cannot complete shared-Source retention acceptance. PURGE and Restore are not part of this capability. Traceability: REQ-PROJECT-018 (partial), DEC-007, AC-PROJECT-018 (partial); C001-S2.

#### Scenario: Delete active Project
- **WHEN** ordinary DELETE targets an active Project at its expected version
- **THEN** the row remains in PostgreSQL with `deleted_at` set, its version increments once, and ordinary list/get no longer return it

#### Scenario: Delete unknown or already deleted Project
- **WHEN** ordinary DELETE targets an unknown or already soft-deleted identifier
- **THEN** the API returns structured HTTP 404 and performs no additional mutation

#### Scenario: Shared-Source retention remains deferred
- **WHEN** CHANGE-001 schema and delete behavior are audited
- **THEN** no Source Content, Source Comment, Evidence, Project-Source join, physical Project delete, cascade, Restore, or PURGE implementation exists, and the shared-Source assertions in AC-PROJECT-018 remain `UNIMPLEMENTED` for CHANGE-003 real PostgreSQL verification

### Requirement: Authoritative Project Snapshot
The API SHALL return a Project Snapshot containing the current Project representation, `project_version`, and Foundation progress derived from authoritative state; it MUST NOT synthesize crawl/model/cluster progress or downstream counts. Traceability: REQ-PROJECT-008 (partial), REQ-SSE-001, AC-PROJECT-008 (partial), AC-SSE-001; C001-S2/S5.

#### Scenario: Snapshot for active Project
- **WHEN** an active Project Snapshot is requested
- **THEN** it returns current status, version, update time, terminal flag, and available Foundation state information from the committed Project

#### Scenario: Snapshot for deleted Project
- **WHEN** a Snapshot is requested for a soft-deleted Project
- **THEN** the ordinary Snapshot capability returns structured HTTP 404

### Requirement: Structured API errors and conflicts
Foundation API failures SHALL use one stable structured problem schema with a machine-readable code, human-readable detail, HTTP status, request correlation identifier, and optional field errors. Validation SHALL use 422, not found 404, and illegal transition or optimistic-version conflict 409. Traceability: explicit CHANGE-001 instruction; C001-S1–S5.

#### Scenario: Optimistic version conflict
- **WHEN** a mutating request carries an expected Project version that no longer matches the committed row
- **THEN** the API returns HTTP 409 with the current version and does not apply the mutation

#### Scenario: Error schema consistency
- **WHEN** validation, not-found, illegal-transition, or conflict errors occur
- **THEN** each response follows the same structured problem contract with a distinct machine code

### Requirement: Project persistence after process restart
Committed Project rows and soft-deletion/state/version values SHALL remain correct across API process restarts because PostgreSQL is the sole persistence authority. Traceability: REQ-FOUNDATION-001, REQ-DATA-001, AC-FOUNDATION-001, AC-DATA-001; C001-S2/S6.

#### Scenario: Restart persistence
- **WHEN** a Project is created or changed, the API process stops, and a new API process connects to the same migrated PostgreSQL database
- **THEN** list/get/Snapshot return the committed values and versions without fixture or in-memory reconstruction
