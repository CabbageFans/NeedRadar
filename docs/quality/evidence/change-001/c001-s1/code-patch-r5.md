# C001-S1 Code Patch R5 Evidence

Date: 2026-09-28

This report is informational. State authority comes from canonical scope, fresh checker execution, and runner-generated JSON receipts under `receipts/`; the prose and exit-code summaries below do not authorize a Requirement result.

## Provenance changes

- Removed the committed/persisted IU grandfather path. Every `IMPLEMENTED_UNVERIFIED` row is checked against the current active Change/Slice and its canonical `FULL` owner on every run.
- Replaced manifest command and exit-code authority with repository-controlled verification target IDs and a fixed pytest runner.
- Replaced source-text Requirement/Acceptance searches with collected `quality_binding` pytest markers and exact node IDs.
- Removed `reviewer_gate` from machine authorization. Independent review remains a process-level Requirement Verification responsibility.
- Bound receipts to the current source fingerprint, complete target-registry hash, and target-definition hash.

## Current C001-S1 IU targets

| Requirement | Target | Structured nodes | Fresh result |
|---|---|---:|---|
| REQ-ARCH-002 | VT-S1-ARCH-002 | 2 | PASS |
| REQ-ARCH-010 | VT-S1-ARCH-010 | 1 | PASS |
| REQ-ARCH-013 | VT-S1-ARCH-013 | 2 | PASS |
| REQ-GOVERNANCE-011 | VT-S1-GOVERNANCE-011 | 1 | PASS |
| REQ-FOUNDATION-001 | VT-S1-FOUNDATION-001 | 2 | PASS |

All five Traceability results remain `IMPLEMENTED_UNVERIFIED`; this patch does not perform Requirement Verification or promote any Requirement to `PASS`.

## Verification summary

- R5 quality-gate unit/adversarial suite: 53 passed, including R5-A01 through R5-A12.
- Full backend unit suite: 95 passed.
- Full PostgreSQL integration suite: 11 passed, including forged-session-marker rejection, guarded test database, migrations, readiness, and structured startup logging.
- API formatting/lint/type checking: passed.
- Web lint/typecheck/unit/build: passed; 1 Vitest passed and the Next.js production build completed.
- OpenAPI snapshot/generated types, S1 scope audit, and strict OpenSpec validation: passed.
- Foundation Playwright E2E: 1 passed against real localhost Web, API, and PostgreSQL.
- Official quality checker: passed while freshly executing all five canonical IU targets.

The database guard also rejected runs with a missing test URL and with `TEST_DATABASE_URL` equal to `DATABASE_URL`; the successful integration and E2E runs used the isolated guarded PostgreSQL endpoint.
