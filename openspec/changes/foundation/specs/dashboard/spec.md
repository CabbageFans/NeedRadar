# Spec Delta

## Purpose

定义 CHANGE-001 的最小 Dashboard 旅程：用户通过真实 Web/API/PostgreSQL 创建并查看空 Project，同时不伪造尚未产生的下游分析指标。

## ADDED Requirements

### Requirement: Empty Project creation journey
The Web SHALL provide a Dashboard new-project entry that collects Project name, original research question, and optional context, calls the real backend create capability, and returns the user to a Dashboard containing the persisted Project. Traceability: REQ-PROJECT-014, AC-PROJECT-014; C001-S4.

#### Scenario: Create from empty Dashboard
- **WHEN** a user opens an empty Dashboard, submits valid Project fields, and creation succeeds
- **THEN** the Dashboard shows the Project returned by the backend and the row exists in PostgreSQL

#### Scenario: Create validation error
- **WHEN** the backend rejects the create payload
- **THEN** the form presents the structured validation details without inserting a local-only or hardcoded Project card

### Requirement: Dashboard uses backend-owned Project facts
Dashboard Project cards SHALL display name, original query, backend status, Foundation progress, latest update time, and a Project navigation action from API data; the frontend MUST NOT infer status or use localStorage, fixtures, or a mock API as the business source of truth. Traceability: REQ-PROJECT-011, REQ-PROJECT-014, REQ-UI-002 (partial), REQ-ARCH-011/012 (partial), AC-PROJECT-011, AC-PROJECT-014, AC-UI-002 (partial); C001-S4.

#### Scenario: Backend status differs from client expectation
- **WHEN** the backend Snapshot reports a status different from any prior client value
- **THEN** the rendered card/detail follows the backend status and version

#### Scenario: Enter Project
- **WHEN** the user activates the Project navigation action
- **THEN** the Web opens the Foundation Project view using the persisted identifier and authoritative Snapshot

### Requirement: Unavailable downstream metrics are not zero
Until their owning future Changes exist, the Dashboard MUST hide Demand Cluster, Evidence, Top Demand, and platform-coverage metrics or label them `尚未分析`, `not available`, or `—`; it MUST NOT display synthetic zeroes that imply completed analysis. Traceability: REQ-UI-002 (partial), REQ-GOVERNANCE-005, AC-UI-002 (partial); C001-S4.

#### Scenario: Newly created empty Project
- **WHEN** a Project has no downstream capability because only Foundation exists
- **THEN** every unavailable downstream metric is hidden or explicitly unavailable and no fake numeric result is rendered

### Requirement: Deleted Projects disappear from ordinary Dashboard
The ordinary Dashboard SHALL exclude soft-deleted Projects and SHALL converge to the backend list/Snapshot after deletion. This is CHANGE-001 partial Project/UI evidence only; it does not satisfy AC-PROJECT-018 shared-Source retention. Traceability: REQ-PROJECT-018 (partial), AC-PROJECT-018 (partial); C001-S4/S5.

#### Scenario: Soft delete from active list
- **WHEN** a Project is soft-deleted through the real API and the Dashboard refreshes or handles its notification
- **THEN** the Project no longer appears while its PostgreSQL row remains

#### Scenario: Direct navigation to deleted Project
- **WHEN** the user navigates to a previously known soft-deleted Project URL
- **THEN** the Web renders the not-found path based on the backend 404 and does not reconstruct cached Project content
