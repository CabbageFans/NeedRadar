# NeedRadar Codex Rules

These rules apply to every repository session. Keep this file concise; the complete business truth remains in `docs/spec/NeedRadar_需求说明书_OpenSpec_v1.0.md`.

## Authority order

1. Explicit new user instruction
2. NeedRadar Spec Baseline
3. User-confirmed entries in `docs/quality/DECISIONS.md`
4. OpenSpec capability specs
5. `docs/quality/ACCEPTANCE.md`
6. `docs/quality/PLAN.md` and OpenSpec tasks
7. Current implementation

`DECISIONS.md` may fill gaps only; it must never override the Spec Baseline. Report conflicts immediately.

## Invariants

- Never silently change, weaken, extend, or reinterpret requirements; preserve MUST/MUST_NOT/SHOULD/MAY strength.
- Never implement future capabilities outside the active OpenSpec Change.
- Never lower an acceptance threshold or delete/disable a failing test to manufacture PASS.
- Every schema change requires a migration. Every LLM prompt is versioned.
- Demand Score logic and every Research Project state transition require tests.
- LLM conclusions must never be presented as measured statistics.
- Evidence traceability from conclusion to original source is mandatory.
- Never claim PASS without running the stated verification and retaining evidence.
- A real external dependency not exercised against the real system is `NOT_VERIFIED` or `BLOCKED`, never PASS; mocks satisfy only non-live test levels.
- Do not modify the Spec Baseline during implementation. Propose requirement changes to the user instead.

