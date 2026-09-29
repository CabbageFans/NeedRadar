# C001-S1 Code Patch R4 Evidence

- Executed: `2026-09-28T09:18:49Z`
- Scope: CHANGE-001 / C001-S1 quality-gate infrastructure only
- Result: implementation verification PASS; no Requirement was changed to `PASS`

## Closed root cause

`IMPLEMENTED_UNVERIFIED` was previously validated as a standalone Result value. The checker accepted any Requirement that had a `FULL` owner somewhere in the registry, so a C001-S2-owned Requirement could be manually written as IU during C001-S1 and later reused as a PASS pre-state.

The checker now requires exactly one repository-controlled Implementation Attestation for every IU row. A new IU transition is authorized only when its canonical `FULL` owner equals the active Change/Slice. A committed IU is considered persisted only when the parent commit already contains the same IU result and attestation reference; the current commit cannot authorize itself merely by containing the forged state.

## Provenance chain

Each attestation records canonical Requirement/Change/Slice/FULL coverage, implementation and test references, requirement/Acceptance test bindings, executed commands and zero exit codes, a scope-and-source fingerprint, and creation time. Traceability implementation/test cells must exactly match it. Referenced files must be repository-relative, non-symlink regular files and remain non-empty.

Requirement Verification now additionally requires `implementation_attestation_ref` and `implementation_attestation_hash`. The committed IU pre-state must reference that exact attestation; its content hash, source fingerprint, canonical owner, required Acceptance IDs, and implementation/test refs are revalidated. Source or attestation changes invalidate the transition.

## Adversarial coverage

| Test | Attack | Result |
|---|---|---|
| QG-IU-001 | S1 DEFERRED Requirement → IU | BLOCKED |
| QG-IU-002 | Manually forged persisted IU without attestation | BLOCKED |
| QG-IU-003 | Wrong-Slice attestation | BLOCKED |
| QG-IU-004 | S2 Requirement reuses unbound S1 tests | BLOCKED |
| QG-IU-005 | PARTIAL → IU | BLOCKED |
| QG-IU-006 | DEFERRED → IU | BLOCKED |
| QG-IU-007 | Cross-Change → IU | BLOCKED |
| QG-IU-008 | Valid C001-S1 FULL Requirement → IU | ALLOWED |
| QG-IU-009 | PASS substitutes a different attestation | BLOCKED |
| QG-IU-010 | Source changes after attestation | BLOCKED |
| QG-IU-011 | Matching IU provenance + independent RV fixture | ALLOWED |
| Reviewer R4 chain | S1 forged IU → switch S2 → reuse S1 refs → PASS | BLOCKED |

## Verification results

| Command | Result |
|---|---|
| `pnpm check` | PASS: Web checks/build, backend formatting/lint/types, OpenAPI, scope, and quality docs |
| `pnpm test:unit` | PASS: backend 83 tests; Web 1 test |
| `uv run pytest apps/api/tests/unit/test_quality_gate.py -q` | PASS: 41 quality-gate tests |
| `pnpm test:integration` with guarded test DB variables | PASS: 11 real PostgreSQL/runtime tests |
| `pnpm test:migration` with guarded test DB variables | PASS: 1 migration cycle test |
| `API_PORT=18123 WEB_PORT=31123 pnpm test:e2e` with guarded test DB variables | PASS: 1 real Foundation E2E test |
| `openspec validate foundation --strict` | PASS |
| `git diff --check` | PASS |

The full unit suite covers forged libpq options, missing/mismatched DB guards, valid guard behavior, local/remote CORS, and structured logging. Integration covers unsafe-target preservation, PostgreSQL migrations/readiness, and real structured Uvicorn startup/access logs. E2E uses alternate loopback ports; product defaults remain Web 3000 and API 8000.

## Scope

`scripts/quality/check_s1_scope.py` reports no business tables, future infrastructure, competing drivers/locks, frontend-backend imports, or client secret names. No C001-S2 business implementation, Research Project, state machine, Dashboard capability, Project SSE, or CHANGE-002+ implementation was added.
