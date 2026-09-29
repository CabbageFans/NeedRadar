# C001-S1 Code Patch R3 Evidence

- Executed: `2026-09-28T16:43:13+08:00`
- Branch: `main`
- HEAD before patch: `9b48714a90bb29aadf29a78e51be1a479b3ffd5a`
- Scope: Quality PASS scope authorization and Traceability policy consistency only
- Verification stage: `CODE_REVIEW_READY`
- Requirement result policy: D-015; no Requirement was changed to `PASS`

## Scope authorization

`docs/quality/verification-scope.json` is a minimal authorization registry. The checker treats evidence scope as a claim and independently validates Requirement → Change → Slice → Acceptance → coverage against the Requirement Index, Acceptance Contract, PLAN, and the current CHANGE-001 proposal/tasks/capability specs. `FULL` is the only coverage eligible for PASS; `PARTIAL`, `SCOPE_GUARD`, and `DEFERRED` are fail-closed.

`docs/quality/VERIFICATION_STATE.json` is the active-scope source. It records `active_change=CHANGE-001`, `active_slice=C001-S1`, and `stage=CODE_REVIEW_READY`. Missing, unknown, or mismatched active scope fails validation. PASS evidence must also bind to the current Git HEAD whose Traceability row was `IMPLEMENTED_UNVERIFIED`; a direct `UNIMPLEMENTED → PASS` transition fails.

## Exploit regression

The automated `test_qg_scope_001_s1_evidence_cannot_pass_s2_requirement` starts from a schema-valid S1 manifest, changes its claimed Requirement to `REQ-DATA-001`, retains valid source/test references and fingerprint, and attempts PASS under active C001-S1. The checker rejects it because the registry records `REQ-DATA-001` as `DEFERRED` for C001-S1 and `FULL` for C001-S2.

The quality-gate suite also rejects S1 evidence aimed at a CHANGE-002 Requirement, a correct Requirement with a wrong Slice, PARTIAL coverage, an unrelated Acceptance, a missing required Acceptance, registry-only self-authorization, fake stage metadata, repository-outside evidence, stale fingerprints, and missing implementation/test references.

## Verification results

| Command / check | Exit | Result |
|---|---:|---|
| `pnpm check` | 0 | Web lint/typecheck/Vitest/build, backend Ruff/mypy, OpenAPI, scope, and quality checker passed. |
| `pnpm test:unit` | 0 | Backend 71 passed; Web 1 passed. |
| `uv run pytest -q apps/api/tests/unit/test_quality_gate.py` | 0 | 29 positive/adversarial quality-gate tests passed. |
| `pnpm test:integration` with explicit guarded test DB URLs | 0 | 11 real PostgreSQL 18.6 tests passed, including DB guard attacks/preservation and real runtime logging. |
| `pnpm test:migration` with explicit guarded test DB URLs | 0 | Empty baseline downgrade/re-upgrade passed. |
| `API_PORT=18123 WEB_PORT=31123 pnpm test:e2e` with explicit guarded test DB URLs | 0 | Real Browser → Web → FastAPI → PostgreSQL Foundation journey passed. |
| `openspec validate foundation --strict` | 0 | CHANGE-001 artifacts are valid. |
| `git diff --check` | 0 | No whitespace errors. |
| `pnpm check:scope` | 0 | No C001-S2–S5 or CHANGE-002+ business leakage. |

Runtime: Node `v24.15.0`, pnpm `10.33.2`, Python `3.11.14`, uv `0.12.2`, PostgreSQL `18.6`.

The default product contract remains Web `3000` and API `8000`. The default development PostgreSQL port `5432` was already occupied, so no user process was stopped and no default was changed; formal integration/E2E used the isolated guarded test database on `55432` and alternate local-only Web/API ports.

## Requirement state

The five S1 `FULL` Requirements remain `IMPLEMENTED_UNVERIFIED`: `REQ-ARCH-002`, `REQ-ARCH-010`, `REQ-ARCH-013`, `REQ-GOVERNANCE-011`, and `REQ-FOUNDATION-001`. Partial, deferred, later-Slice, and cross-Change Requirements remain `UNIMPLEMENTED`.
