# Spec Delta

## Purpose

定义 DEC-006 确认的 13 状态词汇、唯一后端转换入口、失败恢复、终态及单调 Project version 行为，阻止客户端或 repository 任意改写状态。

## ADDED Requirements

### Requirement: Confirmed Project state vocabulary
The backend SHALL represent exactly `DRAFT`, `PLANNING`, `PLAN_READY`, `CRAWLING`, `PAUSED`, `CRAWL_PARTIAL`, `ANALYZING_SIGNALS`, `CLUSTERING`, `CURATING_CLUSTERS`, `SCORING`, `READY`, `FAILED`, and `CANCELLED` as the Foundation Project status vocabulary. Traceability: REQ-PROJECT-009 (`SHOULD` source vocabulary superseded by USER_CONFIRMED DEC-006 exact contract), REQ-PROJECT-016, AC-PROJECT-016; C001-S3.

#### Scenario: Persist and return every confirmed status
- **WHEN** backend-owned state commands place test Projects into each confirmed status
- **THEN** PostgreSQL and API representations use the exact status value without client-side aliases

#### Scenario: Unknown status is rejected
- **WHEN** persistence or API validation encounters a status outside the confirmed vocabulary
- **THEN** the value is rejected rather than stored or rendered as a valid status

### Requirement: One backend transition policy
Every Project status mutation MUST pass through one backend state service that maps a command/action and current state to a permitted target; public clients MUST NOT submit an arbitrary target status and repositories MUST NOT expose an unrestricted status setter. Traceability: REQ-PROJECT-010, REQ-PROJECT-011, REQ-PROJECT-016, AC-PROJECT-010, AC-PROJECT-011, AC-PROJECT-016; C001-S3/S4.

#### Scenario: Allowed command
- **WHEN** an authorized backend command is valid for the current Project status and expected version
- **THEN** the service commits exactly the target defined by the transition policy

#### Scenario: Arbitrary client target
- **WHEN** a client attempts to write `status` or supply a desired target outside a named command contract
- **THEN** the API rejects the request and the Project remains unchanged

#### Scenario: Repository bypass attempt
- **WHEN** code ownership/static tests inspect the Project repository interface
- **THEN** no public general-purpose status mutation path exists outside the state service

### Requirement: Complete legal transition graph
The state service SHALL allow only the DEC-006 transitions enumerated in `design.md`; every unlisted source/target pair MUST be rejected without state, version, timestamp, or event changes. Traceability: REQ-PROJECT-016, REQ-GOVERNANCE-014, AC-PROJECT-016, AC-GOVERNANCE-014; C001-S3.

#### Scenario: Exhaustive allowed and forbidden matrix
- **WHEN** all 169 ordered source/target status pairs are tested against an explicit expected matrix manually derived from DEC-006, this capability spec, and the Acceptance Contract
- **THEN** every expected allowed transition succeeds under its command/preconditions and every expected forbidden pair is rejected, without importing or deriving expected results from the production transition definition

#### Scenario: Production policy and test oracle are independent
- **WHEN** state-test dependencies and fixtures are inspected
- **THEN** production owns its transition definition while tests separately own explicit `EXPECTED_ALLOWED_TRANSITIONS` and `EXPECTED_FORBIDDEN_TRANSITIONS`, and neither expected collection imports, calls, reflects, serializes, or generates from the production table

#### Scenario: Idempotent same-state request is not a transition
- **WHEN** a command would leave status unchanged
- **THEN** it is rejected or treated as an explicit no-op without incrementing version or emitting a state-change event

#### Scenario: Repeated transition command
- **WHEN** an already committed transition command is repeated against the resulting state or with the consumed expected version
- **THEN** the request is rejected or explicitly no-op according to the named command contract and cannot add a second observable mutation/version/event

#### Scenario: Deleted Project rejects state commands
- **WHEN** any state command targets a soft-deleted Project
- **THEN** the ordinary application entry point returns the not-found contract and no state, version, timestamp, or event changes

### Requirement: Failure source and retry
Entering `FAILED` SHALL atomically store the immediate prior status in `failed_from_status`; retry SHALL return only to that stored retryable status, clear `failed_from_status`, and MUST NOT accept a client-selected target. Traceability: REQ-PROJECT-017, DEC-006, AC-PROJECT-017; C001-S3.

#### Scenario: Enter FAILED from retryable stage
- **WHEN** the `fail` command is issued from a retryable source status
- **THEN** status becomes `FAILED`, `failed_from_status` equals the source, and version increments once

#### Scenario: Retry failed Project
- **WHEN** `retry` is issued for a FAILED Project with a valid stored source and matching expected version
- **THEN** status returns only to that stored source, the failure source is cleared, and version increments once

#### Scenario: Invalid retry source
- **WHEN** a FAILED row has a null or non-retryable failure source, or a client supplies another target
- **THEN** retry returns a structured conflict, performs no mutation, and emits no event

### Requirement: CANCELLED is terminal and delete is separate
`CANCELLED` SHALL have no outgoing status transition, Stop and Cancel SHALL share the same terminal Project semantics wherever the confirmed policy permits cancellation, and Project soft delete MUST remain outside the state machine. Traceability: REQ-PROJECT-017, DEC-003/006/007, AC-PROJECT-017; C001-S3.

#### Scenario: Transition from CANCELLED
- **WHEN** any state command, including retry, targets a CANCELLED Project
- **THEN** the backend rejects it without mutation or event

#### Scenario: Delete without state transition
- **WHEN** an active, failed, ready, or cancelled Project is soft-deleted
- **THEN** its status remains unchanged while deletion fields/version follow the Project delete contract

### Requirement: Monotonic integer Project version
Each committed observable Project state or Foundation progress mutation SHALL atomically increment a database integer `project_version` by exactly one; creation SHALL start at 1, failed/conflicting transactions SHALL not consume a version, and timestamps MUST NOT substitute for the version. Traceability: REQ-SSE-002, DEC-008, AC-SSE-002; C001-S3/S5.

#### Scenario: Successful observable mutation
- **WHEN** a valid state change or soft delete commits from version N
- **THEN** the stored Project and emitted notification carry version N+1

#### Scenario: Rolled-back or rejected mutation
- **WHEN** validation, transition policy, optimistic concurrency, or database commit fails
- **THEN** the stored version remains N and no committed-version event is published

#### Scenario: Concurrent writers
- **WHEN** two mutations use the same expected version N
- **THEN** at most one commits as N+1 and the other receives a structured HTTP 409 conflict
