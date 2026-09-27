#!/usr/bin/env python3
"""Validate NeedRadar pre-implementation quality-document references.

Use --write-traceability after intentionally changing the Requirement Catalog.
The generated matrix always contains exactly one row per Requirement.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQ_PATH = ROOT / "docs/quality/REQUIREMENTS_INDEX.md"
AC_PATH = ROOT / "docs/quality/ACCEPTANCE.md"
TRACE_PATH = ROOT / "docs/quality/TRACEABILITY.md"
PLAN_PATH = ROOT / "docs/quality/PLAN.md"

REQ_ID_RE = re.compile(r"REQ-[A-Z]+-\d{3}")
AC_ID_RE = re.compile(r"(?<!REDLINE-)AC-[A-Z]+-\d{3}")
REDLINE_ID_RE = re.compile(r"REDLINE-AC-\d{3}")
RANGE_RE = re.compile(r"\b((?:REQ|AC)-[A-Z]+-)(\d{3})\.\.(\d{3})\b")


def rows(path: Path, prefixes: tuple[str, ...]) -> list[list[str]]:
    parsed: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefixes):
            parsed.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return parsed


def unique(values: list[str], label: str, errors: list[str]) -> None:
    duplicates = sorted(key for key, count in Counter(values).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate {label}: {', '.join(duplicates)}")


def expand_ranges(text: str) -> set[str]:
    expanded: set[str] = set()
    for prefix, start, end in RANGE_RE.findall(text):
        expanded.update(f"{prefix}{value:03d}" for value in range(int(start), int(end) + 1))
    without_ranges = RANGE_RE.sub("", text)
    expanded.update(REQ_ID_RE.findall(without_ranges))
    expanded.update(AC_ID_RE.findall(without_ranges))
    expanded.update(REDLINE_ID_RE.findall(without_ranges))
    return expanded


def load_catalog() -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    catalog: list[dict[str, str]] = []
    for row in rows(REQ_PATH, ("| REQ-",)):
        if len(row) != 8:
            raise ValueError(f"malformed Requirement row: {row}")
        req_id, kind, source, level, summary, acceptance, change, status = row
        catalog.append(
            {
                "id": req_id,
                "kind": kind,
                "source": source,
                "level": level,
                "summary": summary,
                "acceptance": acceptance,
                "change": change,
                "status": status,
            }
        )
    return catalog, {item["id"]: item for item in catalog}


def load_acceptance() -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    contracts: list[dict[str, str]] = []
    for row in rows(AC_PATH, ("| AC-", "| REDLINE-AC-")):
        if len(row) != 7:
            raise ValueError(f"malformed Acceptance row: {row}")
        ac_id, requirement, given, when, then, verification, evidence = row
        contracts.append(
            {
                "id": ac_id,
                "requirement": requirement,
                "given": given,
                "when": when,
                "then": then,
                "verification": verification,
                "evidence": evidence,
            }
        )
    return contracts, {item["id"]: item for item in contracts}


def write_traceability(catalog: list[dict[str, str]], ac_by_id: dict[str, dict[str, str]]) -> None:
    lines = [
        "# Traceability Matrix",
        "",
        "This matrix is generated from the Requirement Index by `scripts/quality/check_quality_docs.py --write-traceability`. Each Requirement has exactly one row. No OpenSpec capability/change artifact or implementation exists yet, so nothing is marked PASS.",
        "",
        "Result enum: `UNIMPLEMENTED`, `IMPLEMENTED_UNVERIFIED`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`.",
        "",
        "Completion reports must separately show: (1) all Requirements, (2) mandatory `ATOMIC` Requirements, and (3) `ROLLUP`/`E2E` gates. Partial work never promotes a full Rollup/E2E Acceptance.",
        "",
        "| Requirement | Acceptance | OpenSpec Capability | Change | Implementation | Test | Evidence | Result |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in catalog:
        acceptance = item["acceptance"]
        verification = "—"
        if acceptance != "No":
            verification = f"Planned {ac_by_id[acceptance]['verification']}"
        else:
            acceptance = f"— ({item['level']})"
        lines.append(
            f"| {item['id']} | {acceptance} | UNASSIGNED | {item['change']} | — | {verification} | — | UNIMPLEMENTED |"
        )
    lines.extend(
        [
            "",
            "## Update rule",
            "",
            "When a Change begins, replace `UNASSIGNED` only with an actual OpenSpec capability identifier. Record concrete implementation/test/evidence references, then change Result only from executed evidence. Real external dependencies not exercised remain `BLOCKED` or `IMPLEMENTED_UNVERIFIED`, never PASS.",
            "",
        ]
    )
    TRACE_PATH.write_text("\n".join(lines), encoding="utf-8")


def validate(catalog: list[dict[str, str]], contracts: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    req_ids = [item["id"] for item in catalog]
    req_set = set(req_ids)
    ac_ids = [item["id"] for item in contracts]
    ac_set = set(ac_ids)
    ac_by_id = {item["id"]: item for item in contracts}
    unique(req_ids, "Requirement IDs", errors)
    unique(ac_ids, "Acceptance IDs", errors)

    allowed_kinds = {"ATOMIC", "SCOPE_GUARD", "ROLLUP", "E2E"}
    allowed_levels = {"MUST", "MUST_NOT", "SHOULD", "MAY"}
    for item in catalog:
        if item["kind"] not in allowed_kinds:
            errors.append(f"invalid Requirement Kind: {item['id']}={item['kind']}")
        if item["level"] not in allowed_levels:
            errors.append(f"invalid Requirement Level: {item['id']}={item['level']}")
        if item["level"] in {"MUST", "MUST_NOT"}:
            if item["acceptance"] == "No":
                errors.append(f"mandatory Requirement missing AC: {item['id']}")
            elif item["acceptance"] not in ac_set:
                errors.append(f"mandatory Requirement references missing AC: {item['id']}->{item['acceptance']}")
        elif item["acceptance"] != "No":
            errors.append(f"SHOULD/MAY incorrectly made acceptance-required: {item['id']}")

    for contract in contracts:
        for req_id in REQ_ID_RE.findall(contract["requirement"]):
            if req_id not in req_set:
                errors.append(f"Acceptance references missing Requirement: {contract['id']}->{req_id}")
    catalog_ac_set = {item["acceptance"] for item in catalog if item["acceptance"] != "No"}
    requirement_ac_set = {item for item in ac_set if not item.startswith("REDLINE-AC-")}
    orphan_requirement_acs = sorted(requirement_ac_set - catalog_ac_set)
    if orphan_requirement_acs:
        errors.append(f"Requirement Acceptance not referenced by Catalog: {', '.join(orphan_requirement_acs)}")

    redlines = sorted(item for item in ac_ids if item.startswith("REDLINE-AC-"))
    expected_redlines = [f"REDLINE-AC-{number:03d}" for number in range(1, 16)]
    if redlines != expected_redlines:
        errors.append("red-line set is not exactly REDLINE-AC-001..015")

    trace_rows = rows(TRACE_PATH, ("| REQ-",))
    trace_req_ids: list[str] = []
    for row in trace_rows:
        if len(row) != 8:
            errors.append(f"malformed Traceability row: {row}")
            continue
        requirement, acceptance, _, _, _, _, _, result = row
        if ".." in requirement or not REQ_ID_RE.fullmatch(requirement):
            errors.append(f"Traceability is not one Requirement per row: {requirement}")
        trace_req_ids.append(requirement)
        if requirement in req_set:
            expected_ac = next(item["acceptance"] for item in catalog if item["id"] == requirement)
            if expected_ac != "No" and acceptance != expected_ac:
                errors.append(f"Traceability AC mismatch: {requirement}->{acceptance}, expected {expected_ac}")
            if expected_ac == "No" and not acceptance.startswith("—"):
                errors.append(f"optional Traceability row should not claim AC: {requirement}->{acceptance}")
        if result == "PASS":
            errors.append(f"pre-implementation Traceability contains PASS: {requirement}")
    unique(trace_req_ids, "Traceability Requirement rows", errors)
    missing_trace = sorted(req_set - set(trace_req_ids))
    orphan_trace = sorted(set(trace_req_ids) - req_set)
    if missing_trace:
        errors.append(f"Requirements missing from Traceability: {', '.join(missing_trace)}")
    if orphan_trace:
        errors.append(f"orphan Traceability Requirements: {', '.join(orphan_trace)}")

    plan_text = PLAN_PATH.read_text(encoding="utf-8")
    plan_refs = expand_ranges(plan_text)
    for reference in sorted(plan_refs):
        if reference.startswith("REQ-") and reference not in req_set:
            errors.append(f"PLAN references missing Requirement: {reference}")
        elif (reference.startswith("AC-") or reference.startswith("REDLINE-AC-")) and reference not in ac_set:
            errors.append(f"PLAN references missing Acceptance: {reference}")

    slice_section = plan_text.split("## CHANGE-001 reviewable slices", 1)[-1].split("### Recommended execution order", 1)[0]
    slice_refs = expand_ranges(slice_section)
    for item in catalog:
        if item["id"] not in slice_refs:
            continue
        cross_change_gate = item["kind"] in {"ROLLUP", "E2E"} and item["change"] != "CHANGE-001"
        if cross_change_gate:
            errors.append(f"cross-Change Rollup/E2E Requirement bound to CHANGE-001 Slice: {item['id']}")
        if item["kind"] == "SCOPE_GUARD":
            errors.append(f"Scope Guard presented as CHANGE-001 Slice outcome: {item['id']}")

    req_by_id = {item["id"]: item for item in catalog}
    for row in rows(PLAN_PATH, ("| 1 | C001-", "| 2 | C001-", "| 3 | C001-", "| 4 | C001-", "| 5 | C001-", "| 6 | C001-")):
        if len(row) != 8:
            errors.append(f"malformed CHANGE-001 Slice row: {row}")
            continue
        acceptance_coverage = expand_ranges(row[4])
        for ac_id in acceptance_coverage:
            if not ac_id.startswith("AC-") or ac_id not in ac_by_id:
                continue
            mapped_requirements = REQ_ID_RE.findall(ac_by_id[ac_id]["requirement"])
            for req_id in mapped_requirements:
                item = req_by_id[req_id]
                cross_change_gate = item["kind"] in {"ROLLUP", "E2E"} and item["change"] != "CHANGE-001"
                if cross_change_gate:
                    errors.append(f"cross-Change Rollup/E2E AC bound to CHANGE-001 Slice: {ac_id}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-traceability", action="store_true")
    args = parser.parse_args()
    catalog, _ = load_catalog()
    contracts, ac_by_id = load_acceptance()
    if args.write_traceability:
        write_traceability(catalog, ac_by_id)
    errors = validate(catalog, contracts)
    if errors:
        print("QUALITY_DOC_CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    kind_counts = Counter(item["kind"] for item in catalog)
    mandatory_atomic = sum(
        1 for item in catalog if item["kind"] == "ATOMIC" and item["level"] in {"MUST", "MUST_NOT"}
    )
    print("QUALITY_DOC_CHECK: PASS")
    print(f"requirements={len(catalog)} mandatory_atomic={mandatory_atomic}")
    print("kinds=" + ",".join(f"{key}:{kind_counts[key]}" for key in sorted(kind_counts)))
    print(f"acceptance={len(contracts)} redlines=15")
    return 0


if __name__ == "__main__":
    sys.exit(main())
