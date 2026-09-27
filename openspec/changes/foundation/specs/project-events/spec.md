# Spec Delta

## Purpose

定义 Project 级 REST Snapshot + SSE Notification 契约：通过 Connect / Buffer / Snapshot / Reconcile 消除建连竞态，使 UI 在初次加载、断线、重复或乱序通知后都能回到 PostgreSQL/API 事实源，同时不引入 durable replay、event store 或消息代理。

## ADDED Requirements

### Requirement: Subscription-ready handshake precedes Snapshot
PostgreSQL and backend REST SHALL remain the source of truth. Initial load SHALL open the Project SSE connection first, wait for `STREAM_READY`, begin buffering Project mutation events, GET the authoritative Snapshot, discard buffered mutation events whose `project_version <= snapshot.project_version`, reconcile newer buffered versions in ascending order, and only then enter live mode. SSE payloads MUST NOT become a second authoritative state store. Traceability: REQ-SSE-001, DEC-008 plus explicit CHANGE-001 Design Patch R1, AC-SSE-001; C001-S5.

#### Scenario: Initial Project page load
- **WHEN** a Project page initializes
- **THEN** the client performs Connect → `STREAM_READY` → Buffer → GET Snapshot → discard/reconcile buffered versions → Live, and never opens a Snapshot-to-stream race window

#### Scenario: STREAM_READY proves subscription establishment
- **WHEN** the server has established the Project subscription for a connection
- **THEN** it emits a `STREAM_READY` control event containing `project_id`, unique `connection_id`, `observed_project_version`, and UTC `occurred_at`, without a `project_version` field or Project mutation

#### Scenario: Snapshot reconciliation
- **WHEN** buffered mutation events exist after Snapshot version N is applied
- **THEN** the client discards every buffered event at version `<= N`, processes versions `> N` in ascending order as notification triggers for authoritative Snapshot recovery, and never treats buffered payload as Project truth

### Requirement: Mutation and transport event semantics are distinct
Each Project mutation event SHALL contain `event_id`, `project_id`, integer `project_version`, `event_type`, UTC `occurred_at`, and object `payload`; its `project_version` MUST equal the version committed in PostgreSQL by that observable mutation. `event_id` identifies one transport event and MUST NOT be used as a Project version. `HEARTBEAT` and `STREAM_READY` are transport/control events: they SHALL contain separate transport identity, connection identity, `project_id`, `observed_project_version`, and time, and MUST NOT increment or claim a mutation `project_version`. Foundation mutation types are only `PROJECT_CREATED`, `PROJECT_UPDATED`, `PROJECT_STATUS_CHANGED`, and `PROJECT_DELETED`. Traceability: REQ-SSE-002, REQ-API-007 (partial), AC-SSE-002, AC-API-007 (partial); C001-S3/S5.

#### Scenario: Project mutation event
- **WHEN** a Project creation, user-visible Foundation field update, status change, Foundation progress change, or soft delete commits
- **THEN** database `project_version` increments exactly once and the corresponding mutation notification carries that committed value and the complete mutation envelope

#### Scenario: Heartbeat is transport-only
- **WHEN** one or more heartbeat intervals pass without a Project mutation
- **THEN** each `HEARTBEAT` may have a unique `event_id` but carries the same `observed_project_version`, and neither the database nor UI current Project version increments

#### Scenario: STREAM_READY is transport-only
- **WHEN** one or more connections become subscription-ready without a Project mutation
- **THEN** each `STREAM_READY` has a connection/transport identity and observed version, has no mutation `project_version`, and leaves database/UI Project version unchanged

#### Scenario: Unsupported future event
- **WHEN** Foundation event schema is audited
- **THEN** no Crawl Job, login, Signal, model batch, Cluster, Score, Opportunity, Report, or evaluation event type is exposed as implemented

### Requirement: Events publish only after commit
Domain mutation notifications SHALL become observable only for successful transactions and SHALL carry the version committed by that same transaction; a rollback MUST emit nothing. Traceability: REQ-SSE-002, DEC-008, AC-SSE-002; C001-S3/S5.

#### Scenario: Successful transaction notification
- **WHEN** a Project mutation and version increment commit
- **THEN** subscribers may receive the committed-version notification only after commit

#### Scenario: Rolled-back transaction
- **WHEN** a Project mutation transaction rolls back
- **THEN** no notification for its tentative version is delivered

### Requirement: Duplicate, stale, and malformed notifications cannot corrupt UI state
The client SHALL ignore a mutation event whose `project_version <= currentVersion`, SHALL not directly replace authoritative Project state from event payload, and SHALL recover from malformed/unknown messages by retaining current state and obtaining a fresh Snapshot when needed. Traceability: REQ-SSE-004, DEC-008, AC-SSE-004; C001-S5.

#### Scenario: Duplicate or stale event arrives
- **WHEN** the client at version N receives a Project mutation event with version less than or equal to N
- **THEN** it ignores the event, performs no duplicate observable application, and keeps version N state

#### Scenario: Newer notification arrives
- **WHEN** the live client receives a valid mutation notification with version greater than its current version
- **THEN** it re-fetches the Project REST Snapshot and adopts only a response whose version is not older than its current state

#### Scenario: Malformed event arrives
- **WHEN** an event fails its mutation/control schema or has an unknown Foundation event type
- **THEN** the client records/observes the protocol error, does not mutate displayed Project facts from that payload, and performs bounded Snapshot recovery rather than crashing

### Requirement: Reconnect repeats the complete handshake
After SSE disconnect at any point, the client SHALL abandon the incomplete stream and repeat Connect → `STREAM_READY` → Buffer → GET Snapshot → Reconcile → Live. Correctness MUST NOT depend on durable event storage, Last-Event-ID replay, historical replay, or Event Sourcing. Traceability: REQ-SSE-003, DEC-008 plus explicit CHANGE-001 Design Patch R1, AC-SSE-003; C001-S5.

#### Scenario: Event is missed while disconnected
- **WHEN** Project state changes during a disconnected interval and the client reconnects
- **THEN** the new subscription-ready handshake and authoritative Snapshot restore the committed state/version without historical replay

#### Scenario: Disconnect during handshake
- **WHEN** the SSE connection drops before reconciliation reaches live mode
- **THEN** the client discards that handshake's buffer/connection identity and starts a completely new handshake rather than continuing from partial state

#### Scenario: Snapshot recovery fails temporarily
- **WHEN** the handshake Snapshot request fails
- **THEN** the client closes the stream, retains its last authoritative state, exposes recoverable connection status, and retries the complete handshake with bounded backoff

### Requirement: Deterministic handshake race coverage
The handshake and reducer SHALL expose a controlled test boundary that can order stream-ready, mutation, Snapshot, drain, duplicate, stale, and disconnect actions without sleep-based timing. Unit/contract tests MAY replace the transport at that boundary, while final C001-S5 E2E MUST still use real SSE and PostgreSQL. Traceability: REQ-SSE-001..004, AC-SSE-001..004; C001-S5.

#### Scenario: RACE-001 mutation before STREAM_READY
- **WHEN** a committed mutation occurs before subscription readiness is acknowledged
- **THEN** the subsequent Snapshot/reconciliation reaches the committed latest version

#### Scenario: RACE-002 mutation after STREAM_READY before Snapshot request
- **WHEN** a committed mutation occurs after `STREAM_READY` but before the Snapshot request begins
- **THEN** its event enters the active handshake buffer and final client state reaches the latest version

#### Scenario: RACE-003 mutation during Snapshot query
- **WHEN** a deterministic barrier pauses the Snapshot query while a committed mutation event arrives
- **THEN** the event remains buffered and Snapshot plus buffered reconciliation reaches the latest version

#### Scenario: RACE-004 mutation after Snapshot response before buffer drain
- **WHEN** a mutation event arrives after the Snapshot response is available but before buffered events finish draining
- **THEN** the event is retained in the same reconciliation cycle and final client state reaches the latest version

#### Scenario: RACE-005 disconnect during handshake
- **WHEN** the stream disconnects at a controlled handshake barrier
- **THEN** the incomplete buffer is abandoned and a fresh complete handshake reaches the authoritative version

#### Scenario: RACE-006 duplicate event
- **WHEN** the same mutation version is delivered more than once
- **THEN** observable Project mutation is not applied more than once

#### Scenario: RACE-007 stale event
- **WHEN** a mutation event has `project_version <= currentVersion`
- **THEN** it cannot replace, regress, or reapply the current state

### Requirement: Heartbeat and connection lifecycle
SSE SHALL send configurable heartbeat messages, preserve current-stream delivery order for committed mutation notifications, and release database/listener/network resources when a client disconnects, the Project becomes unavailable, or the server shuts down. Traceability: REQ-SSE-004, REQ-RESILIENCE-006 (`SHOULD` broader catalog, Foundation subset), AC-SSE-004; C001-S5.

#### Scenario: Idle connection remains observable
- **WHEN** a stream has no Project mutations for one heartbeat interval
- **THEN** the client receives a non-mutating heartbeat and can distinguish an idle live connection from a dead one

#### Scenario: Project-specific stream for missing or deleted Project
- **WHEN** a Project-specific stream is opened for an unknown/soft-deleted Project, or its Project is deleted while connected
- **THEN** the endpoint rejects with not found before streaming or sends the committed delete mutation notification and closes cleanly

#### Scenario: Client disconnect cleanup
- **WHEN** the browser closes or navigates away
- **THEN** the server cancels the subscription and releases its listener/queue without leaving an orphan task
