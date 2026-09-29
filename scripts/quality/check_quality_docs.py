#!/usr/bin/env python3
"""Validate NeedRadar quality-document references and evidence-backed results.

Use --write-traceability after intentionally changing the Requirement Catalog.
The generated matrix always contains exactly one row per Requirement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path

try:
    from scripts.quality.verification_runner import (
        VerificationExecutionError,
        VerificationRuntime,
        canonical_hash,
        load_target_registry,
    )
except ModuleNotFoundError:  # Direct `python scripts/quality/check_quality_docs.py` execution.
    from verification_runner import (  # type: ignore[no-redef]
        VerificationExecutionError,
        VerificationRuntime,
        canonical_hash,
        load_target_registry,
    )

ROOT = Path(__file__).resolve().parents[2]
REQ_PATH = ROOT / "docs/quality/REQUIREMENTS_INDEX.md"
AC_PATH = ROOT / "docs/quality/ACCEPTANCE.md"
TRACE_PATH = ROOT / "docs/quality/TRACEABILITY.md"
PLAN_PATH = ROOT / "docs/quality/PLAN.md"
VERIFICATION_STATE_PATH = ROOT / "docs/quality/VERIFICATION_STATE.json"
VERIFICATION_SCOPE_PATH = ROOT / "docs/quality/verification-scope.json"
VERIFICATION_TARGETS_PATH = ROOT / "docs/quality/verification-targets.json"
FOUNDATION_PROPOSAL_PATH = ROOT / "openspec/changes/foundation/proposal.md"
FOUNDATION_TASKS_PATH = ROOT / "openspec/changes/foundation/tasks.md"
FOUNDATION_SPEC_PATHS = (
    ROOT / "openspec/changes/foundation/specs/application-foundation/spec.md",
    ROOT / "openspec/changes/foundation/specs/dashboard/spec.md",
    ROOT / "openspec/changes/foundation/specs/project-events/spec.md",
    ROOT / "openspec/changes/foundation/specs/project-state/spec.md",
    ROOT / "openspec/changes/foundation/specs/research-project/spec.md",
)
CANONICAL_SCOPE_SOURCE_PATHS = (
    REQ_PATH,
    AC_PATH,
    PLAN_PATH,
    TRACE_PATH,
    FOUNDATION_PROPOSAL_PATH,
    ROOT / "openspec/changes/foundation/design.md",
    FOUNDATION_TASKS_PATH,
    *FOUNDATION_SPEC_PATHS,
)

REQ_ID_RE = re.compile(r"REQ-[A-Z]+-\d{3}")
AC_ID_RE = re.compile(r"(?<!REDLINE-)AC-[A-Z]+-\d{3}")
REDLINE_ID_RE = re.compile(r"REDLINE-AC-\d{3}")
RANGE_RE = re.compile(r"\b((?:REQ|AC)-[A-Z]+-)(\d{3})\.\.(\d{3})\b")
COMPACT_ID_RE = re.compile(r"\b((?:REQ|AC)-[A-Z]+-)(\d{3}(?:/\d{3})+)\b")
BACKTICK_RE = re.compile(r"`([^`]+)`")
ALLOWED_VERIFICATION_STAGES = {
    "IMPLEMENTATION",
    "CODE_REVIEW_READY",
    "REQUIREMENT_VERIFICATION",
}
EVIDENCE_ROOT_RELATIVE = Path("docs/quality/evidence")
IMPLEMENTATION_ATTESTATION_DIRECTORY_NAME = "implementation"
ALLOWED_COVERAGE_TYPES = {"FULL", "PARTIAL", "SCOPE_GUARD", "DEFERRED"}
ALLOWED_VERIFICATION_LEVELS = {
    "STATIC",
    "UNIT",
    "INTEGRATION",
    "CONTRACT",
    "E2E",
    "LIVE_INTEGRATION",
    "MANUAL",
}
REQUIRED_IMPLEMENTATION_ATTESTATION_FIELDS = {
    "schema_version",
    "requirement_id",
    "change_id",
    "slice_id",
    "coverage",
    "implementation_stage",
    "implementation_refs",
    "test_refs",
    "test_bindings",
    "required_acceptance_ids",
    "verification_targets",
    "execution_receipts",
    "source_fingerprint",
    "created_at",
}
REQUIRED_EVIDENCE_FIELDS = {
    "schema_version",
    "requirement_id",
    "acceptance_ids",
    "change_id",
    "slice_id",
    "verification_stage",
    "result",
    "verified_at",
    "git_head",
    "implementation_refs",
    "test_refs",
    "verification_targets",
    "test_bindings",
    "execution_receipts",
    "artifacts",
    "source_fingerprint",
    "implementation_attestation_ref",
    "implementation_attestation_hash",
}

TargetExecutor = Callable[[str, dict[str, object], str], dict[str, object]]


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
    for prefix, values in COMPACT_ID_RE.findall(without_ranges):
        expanded.update(f"{prefix}{value}" for value in values.split("/"))
    without_ranges = COMPACT_ID_RE.sub("", without_ranges)
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


def load_verification_state(path: Path = VERIFICATION_STATE_PATH) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid verification-state metadata: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("verification-state metadata must be a JSON object")
    return value


def load_verification_scope(path: Path = VERIFICATION_SCOPE_PATH) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid verification-scope registry: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("verification-scope registry must be a JSON object")
    return value


def _canonical_acceptance_ids(
    requirement: str, acceptance_by_id: dict[str, dict[str, str]]
) -> list[str]:
    return sorted(
        ac_id
        for ac_id, item in acceptance_by_id.items()
        if not ac_id.startswith("REDLINE-")
        and requirement in REQ_ID_RE.findall(item["requirement"])
    )


def _change_contains(target: str, change: str) -> bool:
    if target == "ALL":
        return True
    match = re.fullmatch(r"CHANGE-(\d{3})", change)
    if match is None:
        return False
    number = int(match.group(1))
    for part in target.split("/"):
        part = part.strip()
        range_match = re.fullmatch(r"CHANGE-(\d{3})\.\.(\d{3})", part)
        if range_match is not None:
            if int(range_match.group(1)) <= number <= int(range_match.group(2)):
                return True
            continue
        direct_match = re.fullmatch(r"CHANGE-(\d{3})", part)
        if direct_match is not None and int(direct_match.group(1)) == number:
            return True
        shorthand_match = re.fullmatch(r"(\d{3})(?:\.\.(\d{3}))?", part)
        if shorthand_match is not None:
            start = int(shorthand_match.group(1))
            end = int(shorthand_match.group(2) or shorthand_match.group(1))
            if start <= number <= end:
                return True
    return False


def _slice_section(text: str, slice_id: str) -> str:
    marker = f"## {slice_id}"
    if marker not in text:
        return ""
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def _proposal_partial_requirements(text: str) -> set[str]:
    marker = "### Partial cross-Change coverage"
    if marker not in text:
        return set()
    section = text.split(marker, 1)[1].split("\n### ", 1)[0]
    return {value for value in expand_ranges(section) if value.startswith("REQ-")}


def _plan_slice_requirements(text: str) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    prefixes = tuple(f"| {number} | C001-" for number in range(1, 7))
    for line in text.splitlines():
        if not line.startswith(prefixes):
            continue
        row = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(row) != 8:
            continue
        slice_match = re.search(r"C\d{3}-S\d+", row[1])
        if slice_match is None:
            continue
        mapping[slice_match.group()] = {
            value for value in expand_ranges(row[3]) if value.startswith("REQ-")
        }
    return mapping


def _spec_binds_requirement_to_slice(requirement: str, slice_id: str) -> bool:
    for path in FOUNDATION_SPEC_PATHS:
        for line in path.read_text(encoding="utf-8").splitlines():
            if requirement in expand_ranges(line) and slice_id in line:
                return True
    return False


def _scope_entry(
    registry: dict[str, object], change: object, slice_id: object, requirement: str
) -> dict[str, object] | None:
    if not isinstance(change, str) or not isinstance(slice_id, str):
        return None
    changes = registry.get("changes")
    if not isinstance(changes, dict):
        return None
    change_entry = changes.get(change)
    if not isinstance(change_entry, dict):
        return None
    slices = change_entry.get("slices")
    if not isinstance(slices, dict):
        return None
    slice_entry = slices.get(slice_id)
    if not isinstance(slice_entry, dict):
        return None
    requirements = slice_entry.get("requirements")
    if not isinstance(requirements, dict):
        return None
    entry = requirements.get(requirement)
    return entry if isinstance(entry, dict) else None


def _full_scope_owners(registry: dict[str, object], requirement: str) -> list[tuple[str, str]]:
    owners: list[tuple[str, str]] = []
    changes = registry.get("changes")
    if not isinstance(changes, dict):
        return owners
    for change_id, change_entry in changes.items():
        if not isinstance(change_id, str) or not isinstance(change_entry, dict):
            continue
        slices = change_entry.get("slices")
        if not isinstance(slices, dict):
            continue
        for slice_id in slices:
            entry = _scope_entry(registry, change_id, slice_id, requirement)
            if entry is not None and entry.get("coverage") == "FULL":
                owners.append((change_id, slice_id))
    return owners


def validate_scope_registry(
    *,
    registry: dict[str, object],
    catalog_by_id: dict[str, dict[str, str]],
    acceptance_by_id: dict[str, dict[str, str]],
    root: Path,
) -> list[str]:
    errors: list[str] = []
    if registry.get("schema_version") != 1:
        errors.append("verification-scope schema_version must equal 1")

    expected_sources = [path.relative_to(ROOT).as_posix() for path in CANONICAL_SCOPE_SOURCE_PATHS]
    if registry.get("canonical_sources") != expected_sources:
        errors.append("verification-scope canonical_sources must match repository authorities")
    for reference in expected_sources:
        repository_file(
            root=root,
            reference=reference,
            label="verification-scope canonical source",
            errors=errors,
        )

    proposal_text = FOUNDATION_PROPOSAL_PATH.read_text(encoding="utf-8")
    tasks_text = FOUNDATION_TASKS_PATH.read_text(encoding="utf-8")
    plan_text = PLAN_PATH.read_text(encoding="utf-8")
    partial_requirements = _proposal_partial_requirements(proposal_text)
    plan_requirements = _plan_slice_requirements(plan_text)
    changes = registry.get("changes")
    if not isinstance(changes, dict) or not changes:
        errors.append("verification-scope changes must be a non-empty object")
        return errors

    full_owners: dict[tuple[str, str], str] = {}
    for change_id, change_entry in changes.items():
        if not isinstance(change_id, str) or not re.fullmatch(r"CHANGE-\d{3}", change_id):
            errors.append(f"invalid verification-scope change: {change_id}")
            continue
        if not isinstance(change_entry, dict) or not isinstance(change_entry.get("slices"), dict):
            errors.append(f"verification-scope change lacks slices: {change_id}")
            continue
        for slice_id, slice_entry in change_entry["slices"].items():
            expected_prefix = f"C{change_id.removeprefix('CHANGE-')}-S"
            if not isinstance(slice_id, str) or not slice_id.startswith(expected_prefix):
                errors.append(f"verification-scope slice/change mismatch: {change_id}/{slice_id}")
                continue
            if change_id == "CHANGE-001" and slice_id not in plan_requirements:
                errors.append(f"verification-scope slice is absent from PLAN: {slice_id}")
            if not isinstance(slice_entry, dict) or not isinstance(
                slice_entry.get("requirements"), dict
            ):
                errors.append(f"verification-scope slice lacks requirements: {slice_id}")
                continue
            task_refs = expand_ranges(_slice_section(tasks_text, slice_id))
            for requirement, entry in slice_entry["requirements"].items():
                if requirement not in catalog_by_id:
                    errors.append(
                        f"verification-scope references unknown Requirement: {requirement}"
                    )
                    continue
                if not isinstance(entry, dict):
                    errors.append(f"verification-scope entry must be an object: {requirement}")
                    continue
                coverage = entry.get("coverage")
                acceptance_ids = entry.get("acceptance_ids")
                if coverage not in ALLOWED_COVERAGE_TYPES:
                    errors.append(f"invalid verification coverage: {requirement}={coverage}")
                    continue
                if not isinstance(acceptance_ids, list) or not all(
                    isinstance(value, str) for value in acceptance_ids
                ):
                    errors.append(
                        f"verification-scope acceptance_ids must be a string list: {requirement}"
                    )
                    continue
                canonical_acceptance = _canonical_acceptance_ids(requirement, acceptance_by_id)
                if sorted(acceptance_ids) != canonical_acceptance:
                    errors.append(
                        "verification-scope Acceptance ownership drift: "
                        f"{requirement} has {sorted(acceptance_ids)}, "
                        f"expected {canonical_acceptance}"
                    )
                catalog_item = catalog_by_id[requirement]
                if not _change_contains(catalog_item["change"], change_id):
                    errors.append(
                        "verification-scope Change ownership drift: "
                        f"{requirement} does not belong to {change_id}"
                    )
                if coverage == "FULL":
                    if catalog_item["kind"] == "SCOPE_GUARD":
                        errors.append(
                            f"SCOPE_GUARD Requirement cannot have FULL coverage: {requirement}"
                        )
                    if requirement in partial_requirements:
                        errors.append(
                            "verification-scope promotes canonical partial Requirement "
                            f"to FULL: {requirement}"
                        )
                    if requirement not in task_refs:
                        errors.append(
                            "verification-scope FULL Requirement is absent from "
                            f"{slice_id} tasks: {requirement}"
                        )
                    planned_slices = {
                        planned_slice
                        for planned_slice, requirements in plan_requirements.items()
                        if requirement in requirements
                    }
                    if planned_slices and slice_id not in planned_slices:
                        errors.append(
                            "verification-scope FULL Requirement conflicts with PLAN: "
                            f"{requirement} belongs to {sorted(planned_slices)}, not {slice_id}"
                        )
                    if not _spec_binds_requirement_to_slice(requirement, slice_id):
                        errors.append(
                            "verification-scope FULL Requirement is absent from "
                            f"{slice_id} specs: {requirement}"
                        )
                    owner_key = (change_id, requirement)
                    previous_owner = full_owners.get(owner_key)
                    if previous_owner is not None and previous_owner != slice_id:
                        errors.append(
                            f"verification-scope has multiple FULL owners for {requirement}: "
                            f"{previous_owner}, {slice_id}"
                        )
                    full_owners[owner_key] = slice_id
                elif coverage == "PARTIAL" and requirement not in partial_requirements:
                    errors.append(
                        "verification-scope PARTIAL entry lacks canonical partial "
                        f"declaration: {requirement}"
                    )
                elif coverage == "SCOPE_GUARD" and catalog_item["kind"] != "SCOPE_GUARD":
                    errors.append(f"non-SCOPE_GUARD Requirement marked SCOPE_GUARD: {requirement}")
    return errors


def evidence_paths(cell: str) -> list[str]:
    return [value for value in BACKTICK_RE.findall(cell) if "/" in value or Path(value).suffix]


def source_fingerprint(root: Path, references: list[str]) -> str:
    aggregate = hashlib.sha256()
    for reference in sorted(set(references)):
        path = root / reference
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        aggregate.update(f"{reference}\0{digest}\n".encode())
    return aggregate.hexdigest()


def implementation_source_fingerprint(
    root: Path,
    *,
    requirement: str,
    change_id: str,
    slice_id: str,
    references: list[str],
) -> str:
    aggregate = hashlib.sha256()
    for field, value in (
        ("requirement_id", requirement),
        ("change_id", change_id),
        ("slice_id", slice_id),
        ("coverage", "FULL"),
    ):
        aggregate.update(f"{field}\0{value}\n".encode())
    for reference in sorted(set(references)):
        path = root / reference
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        aggregate.update(f"{reference}\0{digest}\n".encode())
    return aggregate.hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _traceability_row_from_text(text: str, requirement: str) -> list[str] | None:
    for line in text.splitlines():
        if not line.startswith(f"| {requirement} |"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 8:
            return cells
    return None


def _traceability_result_from_text(text: str, requirement: str) -> str | None:
    row = _traceability_row_from_text(text, requirement)
    return row[-1] if row is not None else None


def git_traceability_result(root: Path, git_head: str, requirement: str) -> str | None:
    completed = subprocess.run(
        ["git", "show", f"{git_head}:docs/quality/TRACEABILITY.md"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    return _traceability_result_from_text(completed.stdout, requirement)


def git_traceability_attestation(root: Path, git_head: str, requirement: str) -> str | None:
    completed = subprocess.run(
        ["git", "show", f"{git_head}:docs/quality/TRACEABILITY.md"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    row = _traceability_row_from_text(completed.stdout, requirement)
    if row is None or row[-1] != "IMPLEMENTED_UNVERIFIED":
        return None
    references = evidence_paths(row[-2])
    return references[0] if len(references) == 1 else None


def git_file_sha256(root: Path, git_head: str, reference: str) -> str | None:
    completed = subprocess.run(
        ["git", "show", f"{git_head}:{reference}"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        return None
    return hashlib.sha256(completed.stdout).hexdigest()


def git_verification_state(root: Path, git_head: str) -> dict[str, object] | None:
    completed = subprocess.run(
        ["git", "show", f"{git_head}:docs/quality/VERIFICATION_STATE.json"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def repository_git_head(root: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def repository_file(
    *,
    root: Path,
    reference: object,
    label: str,
    errors: list[str],
    evidence_only: bool = False,
) -> Path | None:
    if (
        not isinstance(reference, str)
        or not reference
        or Path(reference).is_absolute()
        or ".." in Path(reference).parts
    ):
        errors.append(f"{label} must be a normalized repository-relative path: {reference}")
        return None
    root_resolved = root.resolve()
    candidate = root / reference
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        errors.append(f"{label} does not exist: {reference}")
        return None
    if root_resolved != resolved and root_resolved not in resolved.parents:
        errors.append(f"{label} escapes repository root: {reference}")
        return None
    if candidate.is_symlink():
        errors.append(f"{label} must not be a symlink: {reference}")
        return None
    if evidence_only:
        evidence_root = (root / EVIDENCE_ROOT_RELATIVE).resolve()
        if evidence_root != resolved and evidence_root not in resolved.parents:
            errors.append(f"{label} is outside docs/quality/evidence: {reference}")
            return None
    if not resolved.is_file():
        errors.append(f"{label} is not a regular file: {reference}")
        return None
    if resolved.stat().st_size == 0:
        errors.append(f"{label} is empty: {reference}")
        return None
    return resolved


def _string_list(manifest: dict[str, object], field: str, errors: list[str]) -> list[str]:
    value = manifest.get(field)
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
    ):
        errors.append(f"evidence manifest {field} must be a non-empty string list")
        return []
    return list(value)


def validate_verification_target_registry(
    *,
    registry: dict[str, object],
    catalog_by_id: dict[str, dict[str, str]],
    acceptance_by_id: dict[str, dict[str, str]],
    scope_registry: dict[str, object],
    root: Path,
    active_change: str | None = None,
    active_slice: str | None = None,
) -> list[str]:
    """Validate the repository-controlled executable target allowlist."""

    errors: list[str] = []
    if registry.get("schema_version") != 1:
        errors.append("verification-target registry schema_version must equal 1")
    targets = registry.get("targets")
    if not isinstance(targets, dict) or not targets:
        return [*errors, "verification-target registry targets must be a non-empty object"]
    receipt_paths: set[str] = set()
    rv_targets_by_requirement: dict[str, list[dict[str, object]]] = {}
    for target_id, target in targets.items():
        if not isinstance(target_id, str) or not re.fullmatch(r"VT-[A-Z0-9-]+", target_id):
            errors.append(f"invalid verification target ID: {target_id}")
            continue
        if not isinstance(target, dict):
            errors.append(f"verification target must be an object: {target_id}")
            continue
        required = {
            "requirement_id",
            "acceptance_ids",
            "change_id",
            "slice_id",
            "verification_stage",
            "verification_level",
            "runner",
            "setup",
            "working_directory",
            "arguments",
            "test_nodes",
            "receipt_path",
        }
        if set(target) != required:
            errors.append(
                f"verification target fields must equal the canonical schema: {target_id}"
            )
            continue
        requirement = target.get("requirement_id")
        acceptance_ids = target.get("acceptance_ids")
        change_id = target.get("change_id")
        slice_id = target.get("slice_id")
        if requirement not in catalog_by_id:
            errors.append(f"verification target has unknown Requirement: {target_id}")
            continue
        owner = _full_scope_owners(scope_registry, str(requirement))
        if owner != [(change_id, slice_id)]:
            errors.append(f"verification target does not match canonical FULL owner: {target_id}")
        scope_entry = _scope_entry(scope_registry, change_id, slice_id, str(requirement))
        expected_acceptance = scope_entry.get("acceptance_ids", []) if scope_entry else []
        if acceptance_ids != expected_acceptance:
            errors.append(f"verification target Acceptance ownership mismatch: {target_id}")
        if not isinstance(acceptance_ids, list):
            errors.append(f"verification target acceptance_ids must be a list: {target_id}")
        else:
            for acceptance_id in acceptance_ids:
                acceptance = acceptance_by_id.get(acceptance_id)
                if acceptance is None or requirement not in REQ_ID_RE.findall(
                    acceptance["requirement"]
                ):
                    errors.append(
                        f"verification target AC does not belong to Requirement: "
                        f"{target_id}->{acceptance_id}"
                    )
        if target.get("verification_stage") not in {
            "IMPLEMENTATION",
            "REQUIREMENT_VERIFICATION",
        }:
            errors.append(f"invalid verification target stage: {target_id}")
        verification_level = target.get("verification_level")
        if verification_level not in ALLOWED_VERIFICATION_LEVELS:
            errors.append(f"invalid verification target level: {target_id}")
        if target.get("verification_stage") == "REQUIREMENT_VERIFICATION":
            rv_targets_by_requirement.setdefault(str(requirement), []).append(target)
            required_levels = {
                acceptance_by_id[acceptance_id]["verification"]
                for acceptance_id in acceptance_ids or []
                if acceptance_id in acceptance_by_id
            }
            if required_levels and required_levels != {verification_level}:
                errors.append(
                    f"Requirement Verification target level does not match its AC: {target_id}"
                )
        if target.get("runner") != "pytest":
            errors.append(f"verification target runner must be pytest: {target_id}")
        if target.get("setup") not in {"none", "guarded_postgres"}:
            errors.append(f"invalid verification target setup: {target_id}")
        if target.get("working_directory") != ".":
            errors.append(f"verification target working_directory must be '.': {target_id}")
        arguments = target.get("arguments")
        nodes = target.get("test_nodes")
        if (
            not isinstance(arguments, list)
            or not arguments
            or not all(isinstance(value, str) and "::" in value for value in arguments)
        ):
            errors.append(
                f"verification target arguments must be exact pytest node IDs: {target_id}"
            )
            arguments = []
        if not isinstance(nodes, list) or not nodes:
            errors.append(f"verification target test_nodes must be non-empty: {target_id}")
            nodes = []
        expected_nodes: list[str] = []
        for node in nodes:
            if not isinstance(node, dict) or set(node) != {
                "nodeid",
                "requirement_id",
                "acceptance_ids",
            }:
                errors.append(f"invalid verification target test node: {target_id}")
                continue
            expected_nodes.append(str(node.get("nodeid")))
            if node.get("requirement_id") != requirement:
                errors.append(f"verification target node Requirement mismatch: {target_id}")
            node_acceptance = node.get("acceptance_ids")
            if not isinstance(node_acceptance, list) or not set(node_acceptance) <= set(
                acceptance_ids or []
            ):
                errors.append(f"verification target node Acceptance mismatch: {target_id}")
            node_path = str(node.get("nodeid", "")).split("::", 1)[0]
            repository_file(
                root=root,
                reference=node_path,
                label=f"verification target node source for {target_id}",
                errors=errors,
            )
        if arguments != expected_nodes:
            errors.append(
                f"verification target arguments must equal declared node IDs: {target_id}"
            )
        covered_acceptance = {
            acceptance_id
            for node in nodes
            if isinstance(node, dict)
            for acceptance_id in node.get("acceptance_ids", [])
            if isinstance(acceptance_id, str)
        }
        if set(acceptance_ids or []) != covered_acceptance:
            errors.append(f"verification target nodes do not cover every AC: {target_id}")
        receipt_path = target.get("receipt_path")
        if (
            not isinstance(receipt_path, str)
            or not receipt_path.startswith("docs/quality/evidence/")
            or not receipt_path.endswith(".json")
            or ".." in Path(receipt_path).parts
        ):
            errors.append(f"invalid verification target receipt_path: {target_id}")
        elif receipt_path in receipt_paths:
            errors.append(f"duplicate verification target receipt_path: {receipt_path}")
        else:
            receipt_paths.add(receipt_path)

    if active_change is not None and active_slice is not None:
        active_requirements = (
            scope_registry.get("changes", {})
            .get(active_change, {})
            .get("slices", {})
            .get(active_slice, {})
            .get("requirements", {})
        )
        if not isinstance(active_requirements, dict):
            errors.append("active Requirement Verification target scope is invalid")
        else:
            for requirement, scope_entry in active_requirements.items():
                if not isinstance(scope_entry, dict) or scope_entry.get("coverage") != "FULL":
                    continue
                requirement_targets = rv_targets_by_requirement.get(requirement, [])
                if not requirement_targets:
                    errors.append(
                        "FULL Requirement lacks canonical REQUIREMENT_VERIFICATION target: "
                        f"{requirement}"
                    )
                    continue
                covered_acceptance = {
                    acceptance_id
                    for target in requirement_targets
                    for acceptance_id in target.get("acceptance_ids", [])
                    if isinstance(acceptance_id, str)
                }
                required_acceptance = set(scope_entry.get("acceptance_ids", []))
                if covered_acceptance != required_acceptance:
                    errors.append(
                        "Requirement Verification targets do not cover mandatory ACs: "
                        f"{requirement}"
                    )
    return errors


def _execute_target(
    executor: TargetExecutor,
    *,
    target_id: str,
    target: dict[str, object],
    source_fingerprint_value: str,
) -> dict[str, object] | None:
    try:
        return executor(target_id, target, source_fingerprint_value)
    except (OSError, ValueError, VerificationExecutionError):
        return None


def validate_execution_receipt(
    *,
    target_id: str,
    target: dict[str, object],
    receipt: dict[str, object] | None,
    source_fingerprint_value: str,
    target_registry: dict[str, object],
    errors: list[str],
) -> None:
    """Validate a receipt created by the trusted runner, never manifest claims."""

    if receipt is None:
        errors.append(f"canonical verification target could not execute: {target_id}")
        return
    expected_nodes = target.get("test_nodes", [])
    expected_nodeids = [node.get("nodeid") for node in expected_nodes if isinstance(node, dict)]
    expected_bindings: list[dict[str, object]] = []
    all_targets = target_registry.get("targets", {})
    if isinstance(all_targets, dict):
        for candidate in all_targets.values():
            if not isinstance(candidate, dict):
                continue
            for node in candidate.get("test_nodes", []):
                if isinstance(node, dict) and node.get("nodeid") in expected_nodeids:
                    binding = {
                        "nodeid": node.get("nodeid"),
                        "requirement_id": node.get("requirement_id"),
                        "acceptance_ids": node.get("acceptance_ids"),
                    }
                    if binding not in expected_bindings:
                        expected_bindings.append(binding)
    expected = {
        "schema_version": 2,
        "target_id": target_id,
        "requirement_id": target.get("requirement_id"),
        "acceptance_ids": target.get("acceptance_ids"),
        "verification_stage": target.get("verification_stage"),
        "verification_level": target.get("verification_level"),
        "target_registry_hash": canonical_hash(target_registry),
        "target_definition_hash": canonical_hash(target),
        "source_fingerprint": source_fingerprint_value,
        "collection_exit_code": 0,
        "collected_nodes": expected_nodeids,
        "actual_exit_code": 0,
        "test_results": {nodeid: "passed" for nodeid in expected_nodeids},
        "working_directory": ".",
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            errors.append(f"runner receipt {field} mismatch for {target_id}")
    actual_bindings = receipt.get("collected_bindings")

    def binding_sort_key(item: dict[str, object]) -> tuple[str, str, str]:
        return (
            str(item.get("nodeid")),
            str(item.get("requirement_id")),
            json.dumps(item.get("acceptance_ids"), sort_keys=True),
        )

    if (
        not isinstance(actual_bindings, list)
        or not all(isinstance(item, dict) for item in actual_bindings)
        or sorted(actual_bindings, key=binding_sort_key)
        != sorted(expected_bindings, key=binding_sort_key)
    ):
        errors.append(f"runner collected bindings mismatch for {target_id}")
    argv = receipt.get("exact_executable_argv")
    if not isinstance(argv, list) or argv[-len(expected_nodeids) :] != expected_nodeids:
        errors.append(f"runner did not execute exact canonical pytest nodes: {target_id}")
    for field in (
        "receipt_id",
        "verification_base_head",
        "executed_at",
        "started_at",
        "finished_at",
        "stdout_sha256",
        "stderr_sha256",
    ):
        if not isinstance(receipt.get(field), str) or not receipt[field]:
            errors.append(f"runner receipt lacks {field}: {target_id}")
    verification_base_head = receipt.get("verification_base_head")
    if not isinstance(verification_base_head, str) or not re.fullmatch(
        r"[0-9a-f]{40}", verification_base_head
    ):
        errors.append(f"runner receipt has invalid verification_base_head: {target_id}")


def validate_recorded_receipts(
    *,
    manifest: dict[str, object],
    target_ids: list[str],
    target_registry: dict[str, object],
    source_fingerprint_value: str,
    root: Path,
    errors: list[str],
    expected_verification_base_head: str | None = None,
) -> None:
    """Validate retained audit receipts; fresh runner results remain the authority."""

    recorded = manifest.get("execution_receipts")
    if not isinstance(recorded, list) or len(recorded) != len(target_ids):
        errors.append("execution_receipts must record every verification target exactly once")
        return
    targets = target_registry.get("targets", {})
    seen: set[str] = set()
    for entry in recorded:
        if not isinstance(entry, dict) or set(entry) != {
            "target_id",
            "receipt_ref",
            "receipt_hash",
        }:
            errors.append("each execution receipt reference has invalid fields")
            continue
        target_id = entry.get("target_id")
        if target_id not in target_ids or target_id in seen:
            errors.append(f"unexpected or duplicate execution receipt target: {target_id}")
            continue
        seen.add(str(target_id))
        target = targets.get(target_id) if isinstance(targets, dict) else None
        if not isinstance(target, dict) or entry.get("receipt_ref") != target.get("receipt_path"):
            errors.append(f"execution receipt path is not canonical: {target_id}")
            continue
        receipt_path = repository_file(
            root=root,
            reference=entry.get("receipt_ref"),
            label=f"execution receipt for {target_id}",
            errors=errors,
            evidence_only=True,
        )
        if receipt_path is None:
            continue
        if entry.get("receipt_hash") != file_sha256(receipt_path):
            errors.append(f"execution receipt hash mismatch: {target_id}")
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"execution receipt is invalid JSON: {target_id}")
            continue
        if not isinstance(receipt, dict):
            errors.append(f"execution receipt must be an object: {target_id}")
            continue
        if receipt.get("source_fingerprint") != source_fingerprint_value:
            errors.append(f"execution receipt source fingerprint is stale: {target_id}")
        if receipt.get("target_definition_hash") != canonical_hash(target):
            errors.append(f"execution receipt target definition is stale: {target_id}")
        if receipt.get("target_registry_hash") != canonical_hash(target_registry):
            errors.append(f"execution receipt target registry is stale: {target_id}")
        if (
            target.get("verification_stage") == "REQUIREMENT_VERIFICATION"
            and receipt.get("verification_base_head") != expected_verification_base_head
        ):
            errors.append(
                f"Requirement Verification receipt is not bound to verification base: {target_id}"
            )
        validate_execution_receipt(
            target_id=str(target_id),
            target=target,
            receipt=receipt,
            source_fingerprint_value=source_fingerprint_value,
            target_registry=target_registry,
            errors=errors,
        )


def validate_implementation_attestation(
    *,
    requirement: str,
    attestation_reference: str,
    catalog_item: dict[str, str] | None,
    scope_registry: dict[str, object],
    target_registry: dict[str, object],
    target_executor: TargetExecutor,
    root: Path,
    expected_active_change: object | None = None,
    expected_active_slice: object | None = None,
) -> tuple[list[str], dict[str, object] | None, Path | None]:
    errors: list[str] = []
    path = repository_file(
        root=root,
        reference=attestation_reference,
        label="Implementation Attestation",
        errors=errors,
        evidence_only=True,
    )
    reference_path = Path(attestation_reference)
    if (
        reference_path.suffix != ".json"
        or IMPLEMENTATION_ATTESTATION_DIRECTORY_NAME not in reference_path.parts
    ):
        errors.append(
            "Implementation Attestation must be a JSON file in an implementation directory"
        )
    if path is None:
        return errors, None, None
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        errors.append(f"Implementation Attestation is not valid JSON: {attestation_reference}")
        return errors, None, path
    if not isinstance(manifest, dict):
        errors.append("Implementation Attestation must be a JSON object")
        return errors, None, path
    missing = sorted(REQUIRED_IMPLEMENTATION_ATTESTATION_FIELDS - set(manifest))
    if missing:
        errors.append("Implementation Attestation missing fields: " + ", ".join(missing))

    owners = _full_scope_owners(scope_registry, requirement)
    if len(owners) != 1:
        errors.append(
            f"Implementation Attestation requires exactly one canonical FULL owner: {requirement}"
        )
        return errors, manifest, path
    canonical_change, canonical_slice = owners[0]
    scope_entry = _scope_entry(scope_registry, canonical_change, canonical_slice, requirement)
    required_acceptance_ids = (
        list(scope_entry.get("acceptance_ids", [])) if scope_entry is not None else []
    )
    expectations = {
        "schema_version": 2,
        "requirement_id": requirement,
        "change_id": canonical_change,
        "slice_id": canonical_slice,
        "coverage": "FULL",
        "implementation_stage": "IMPLEMENTATION",
        "required_acceptance_ids": required_acceptance_ids,
    }
    for field, expected in expectations.items():
        if manifest.get(field) != expected:
            errors.append(f"Implementation Attestation {field} must equal {expected!r}")
    if catalog_item is None or not _change_contains(catalog_item["change"], canonical_change):
        errors.append(
            f"Implementation Attestation Requirement does not belong to {canonical_change}: "
            f"{requirement}"
        )
    if expected_active_change is not None and canonical_change != expected_active_change:
        errors.append(
            "IMPLEMENTED_UNVERIFIED transition requires canonical owner in active Change: "
            f"{requirement}={canonical_change}, active={expected_active_change}"
        )
    if expected_active_slice is not None and canonical_slice != expected_active_slice:
        errors.append(
            "IMPLEMENTED_UNVERIFIED transition requires canonical FULL owner in active Slice: "
            f"{requirement}={canonical_slice}, active={expected_active_slice}"
        )
    if not isinstance(manifest.get("created_at"), str) or not manifest["created_at"]:
        errors.append("Implementation Attestation created_at must be non-empty")

    implementation_refs = _string_list(manifest, "implementation_refs", errors)
    test_refs = _string_list(manifest, "test_refs", errors)
    source_ref_errors_before = len(errors)
    for label, references in (
        ("implementation ref", implementation_refs),
        ("test ref", test_refs),
    ):
        for reference in references:
            repository_file(root=root, reference=reference, label=label, errors=errors)

    bindings = manifest.get("test_bindings")
    declared_bindings: list[dict[str, object]] = []
    bound_acceptance_ids: set[str] = set()
    if not isinstance(bindings, list) or not bindings:
        errors.append("Implementation Attestation test_bindings must be non-empty")
    else:
        for binding in bindings:
            if not isinstance(binding, dict) or set(binding) != {
                "target_id",
                "test_nodeid",
                "requirement_id",
                "acceptance_ids",
            }:
                errors.append(
                    "each Implementation Attestation test binding must contain only "
                    "target_id/test_nodeid/requirement_id/acceptance_ids"
                )
                continue
            test_nodeid = binding.get("test_nodeid")
            acceptance_ids = binding.get("acceptance_ids")
            if binding.get("requirement_id") != requirement:
                errors.append(
                    f"Implementation Attestation test binding Requirement mismatch: {test_nodeid}"
                )
            if (
                not isinstance(acceptance_ids, list)
                or not all(isinstance(item, str) and item for item in acceptance_ids)
                or not set(acceptance_ids) <= set(required_acceptance_ids)
            ):
                errors.append(
                    "Implementation Attestation test binding has invalid Acceptance IDs: "
                    f"{test_nodeid}"
                )
                continue
            if not isinstance(test_nodeid, str) or "::" not in test_nodeid:
                errors.append("Implementation Attestation test binding needs an exact node ID")
                continue
            declared_bindings.append(binding)
            bound_acceptance_ids.update(acceptance_ids)
    if set(required_acceptance_ids) != bound_acceptance_ids:
        errors.append(
            "Implementation Attestation test bindings must cover all required Acceptance IDs"
        )

    references = implementation_refs + test_refs
    fingerprint_value = manifest.get("source_fingerprint")
    if references and len(errors) == source_ref_errors_before:
        expected_fingerprint = implementation_source_fingerprint(
            root,
            requirement=requirement,
            change_id=canonical_change,
            slice_id=canonical_slice,
            references=references,
        )
        if fingerprint_value != expected_fingerprint:
            errors.append(
                "Implementation Attestation source_fingerprint does not match canonical scope "
                "and current sources"
            )
    target_ids = _string_list(manifest, "verification_targets", errors)
    targets = target_registry.get("targets")
    expected_bindings: list[dict[str, object]] = []
    target_acceptance: set[str] = set()
    for target_id in target_ids:
        target = targets.get(target_id) if isinstance(targets, dict) else None
        if not isinstance(target, dict):
            errors.append(f"Implementation Attestation references unknown target: {target_id}")
            continue
        for field, expected in (
            ("requirement_id", requirement),
            ("change_id", canonical_change),
            ("slice_id", canonical_slice),
            ("verification_stage", "IMPLEMENTATION"),
        ):
            if target.get(field) != expected:
                errors.append(f"Implementation Attestation target {field} mismatch: {target_id}")
        target_acceptance.update(target.get("acceptance_ids", []))
        for node in target.get("test_nodes", []):
            if isinstance(node, dict):
                node_source = str(node.get("nodeid", "")).split("::", 1)[0]
                if node_source not in test_refs:
                    errors.append(
                        "Implementation Attestation target node source is not a "
                        f"fingerprinted test_ref: {target_id}->{node_source}"
                    )
                expected_bindings.append(
                    {
                        "target_id": target_id,
                        "test_nodeid": node.get("nodeid"),
                        "requirement_id": node.get("requirement_id"),
                        "acceptance_ids": node.get("acceptance_ids"),
                    }
                )
        if isinstance(fingerprint_value, str):
            receipt = _execute_target(
                target_executor,
                target_id=target_id,
                target=target,
                source_fingerprint_value=fingerprint_value,
            )
            validate_execution_receipt(
                target_id=target_id,
                target=target,
                receipt=receipt,
                source_fingerprint_value=fingerprint_value,
                target_registry=target_registry,
                errors=errors,
            )
    if set(required_acceptance_ids) != target_acceptance:
        errors.append("Implementation Attestation targets must cover all required Acceptance IDs")
    if declared_bindings != expected_bindings:
        errors.append(
            "Implementation Attestation test_bindings must exactly match canonical target nodes"
        )
    if isinstance(fingerprint_value, str):
        validate_recorded_receipts(
            manifest=manifest,
            target_ids=target_ids,
            target_registry=target_registry,
            source_fingerprint_value=fingerprint_value,
            root=root,
            errors=errors,
        )
    return errors, manifest, path


def validate_pass_manifest(
    *,
    requirement: str,
    evidence_reference: str,
    required_acceptance_ids: list[str],
    verification_state: dict[str, object],
    catalog_item: dict[str, str] | None,
    scope_registry: dict[str, object],
    target_registry: dict[str, object],
    target_executor: TargetExecutor,
    root: Path,
    prior_result_lookup: Callable[[Path, str, str], str | None] = git_traceability_result,
    prior_attestation_lookup: Callable[[Path, str, str], str | None] = git_traceability_attestation,
    prior_attestation_hash_lookup: Callable[[Path, str, str], str | None] = git_file_sha256,
    prior_verification_state_lookup: Callable[
        [Path, str], dict[str, object] | None
    ] = git_verification_state,
    current_head_lookup: Callable[[Path], str | None] = repository_git_head,
) -> list[str]:
    errors: list[str] = []
    path = repository_file(
        root=root,
        reference=evidence_reference,
        label="Requirement Verification evidence",
        errors=errors,
        evidence_only=True,
    )
    if path is None:
        return errors
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        errors.append(f"Requirement Verification evidence is not valid JSON: {evidence_reference}")
        return errors
    if not isinstance(manifest, dict):
        errors.append("Requirement Verification evidence must be a JSON object")
        return errors
    missing = sorted(REQUIRED_EVIDENCE_FIELDS - set(manifest))
    if missing:
        errors.append("Requirement Verification evidence missing fields: " + ", ".join(missing))
    scalar_expectations = {
        "schema_version": 2,
        "requirement_id": requirement,
        "acceptance_ids": required_acceptance_ids,
        "change_id": verification_state.get("active_change"),
        "slice_id": verification_state.get("active_slice"),
        "verification_stage": "REQUIREMENT_VERIFICATION",
        "result": "PASS",
    }
    for field, expected in scalar_expectations.items():
        if manifest.get(field) != expected:
            errors.append(f"evidence manifest {field} must equal {expected!r}")
    for field in ("verified_at",):
        if not isinstance(manifest.get(field), str) or not manifest[field]:
            errors.append(f"evidence manifest {field} must be non-empty")
    git_head = manifest.get("git_head")
    prior_attestation_reference: str | None = None
    prior_attestation_hash: str | None = None
    if not isinstance(git_head, str) or not re.fullmatch(r"[0-9a-f]{40}", git_head):
        errors.append("evidence manifest git_head must be a 40-character lowercase SHA")
    else:
        if current_head_lookup(root) != git_head:
            errors.append("evidence manifest git_head must equal repository HEAD")
        prior_verification_state = prior_verification_state_lookup(root, git_head)
        if prior_verification_state is None:
            errors.append("PASS transition requires committed verification-state metadata")
        else:
            for field in ("active_change", "active_slice", "result_update_authority"):
                expected = verification_state.get(field)
                if prior_verification_state.get(field) != expected:
                    errors.append(
                        "IMPLEMENTED_UNVERIFIED pre-state scope does not match current "
                        f"Requirement Verification scope: {field}"
                    )
        if prior_result_lookup(root, git_head, requirement) != "IMPLEMENTED_UNVERIFIED":
            errors.append(
                "PASS transition requires git_head Traceability state "
                f"IMPLEMENTED_UNVERIFIED: {requirement}"
            )
        prior_attestation_reference = prior_attestation_lookup(root, git_head, requirement)
        if prior_attestation_reference is None:
            errors.append(
                "PASS transition requires git_head Traceability to reference exactly one "
                f"Implementation Attestation: {requirement}"
            )
        else:
            prior_attestation_hash = prior_attestation_hash_lookup(
                root, git_head, prior_attestation_reference
            )
            if prior_attestation_hash is None:
                errors.append(
                    "PASS transition requires the committed Implementation Attestation content"
                )
    implementation_refs = _string_list(manifest, "implementation_refs", errors)
    test_refs = _string_list(manifest, "test_refs", errors)
    artifacts = _string_list(manifest, "artifacts", errors)
    for label, references in (
        ("implementation ref", implementation_refs),
        ("test ref", test_refs),
        ("artifact", artifacts),
    ):
        for reference in references:
            repository_file(root=root, reference=reference, label=label, errors=errors)
    attestation_reference = manifest.get("implementation_attestation_ref")
    if attestation_reference != prior_attestation_reference:
        errors.append(
            "Requirement Verification must reference the Implementation Attestation "
            "recorded by the IMPLEMENTED_UNVERIFIED pre-state"
        )
    if not isinstance(attestation_reference, str):
        errors.append("implementation_attestation_ref must be a repository-relative path")
        return errors
    attestation_errors, attestation, attestation_path = validate_implementation_attestation(
        requirement=requirement,
        attestation_reference=attestation_reference,
        catalog_item=catalog_item,
        scope_registry=scope_registry,
        target_registry=target_registry,
        target_executor=target_executor,
        root=root,
        expected_active_change=verification_state.get("active_change"),
        expected_active_slice=verification_state.get("active_slice"),
    )
    errors.extend(attestation_errors)
    if attestation_path is not None:
        current_attestation_hash = file_sha256(attestation_path)
        if manifest.get("implementation_attestation_hash") != current_attestation_hash:
            errors.append("implementation_attestation_hash does not match attestation content")
        if (
            prior_attestation_hash is not None
            and current_attestation_hash != prior_attestation_hash
        ):
            errors.append("Implementation Attestation content changed after IMPLEMENTED_UNVERIFIED")
    if attestation is not None:
        if implementation_refs != attestation.get("implementation_refs"):
            errors.append(
                "Requirement Verification implementation_refs must match Implementation Attestation"
            )
        if test_refs != attestation.get("test_refs"):
            errors.append(
                "Requirement Verification test_refs must match Implementation Attestation"
            )
        if manifest.get("source_fingerprint") != attestation.get("source_fingerprint"):
            errors.append(
                "Requirement Verification source_fingerprint must match Implementation Attestation"
            )
    target_ids = _string_list(manifest, "verification_targets", errors)
    targets = target_registry.get("targets")
    expected_bindings: list[dict[str, object]] = []
    target_acceptance: set[str] = set()
    fingerprint_value = manifest.get("source_fingerprint")
    for target_id in target_ids:
        target = targets.get(target_id) if isinstance(targets, dict) else None
        if not isinstance(target, dict):
            errors.append(f"Requirement Verification references unknown target: {target_id}")
            continue
        for field, expected in (
            ("requirement_id", requirement),
            ("change_id", verification_state.get("active_change")),
            ("slice_id", verification_state.get("active_slice")),
            ("verification_stage", "REQUIREMENT_VERIFICATION"),
        ):
            if target.get(field) != expected:
                errors.append(f"Requirement Verification target {field} mismatch: {target_id}")
        acceptance_values = target.get("acceptance_ids")
        if isinstance(acceptance_values, list):
            target_acceptance.update(value for value in acceptance_values if isinstance(value, str))
        for node in target.get("test_nodes", []):
            if isinstance(node, dict):
                node_source = str(node.get("nodeid", "")).split("::", 1)[0]
                if node_source not in test_refs:
                    errors.append(
                        "Requirement Verification target node source is not a "
                        f"fingerprinted test_ref: {target_id}->{node_source}"
                    )
                expected_bindings.append(
                    {
                        "target_id": target_id,
                        "test_nodeid": node.get("nodeid"),
                        "requirement_id": node.get("requirement_id"),
                        "acceptance_ids": node.get("acceptance_ids"),
                    }
                )
        if isinstance(fingerprint_value, str):
            receipt = _execute_target(
                target_executor,
                target_id=target_id,
                target=target,
                source_fingerprint_value=fingerprint_value,
            )
            validate_execution_receipt(
                target_id=target_id,
                target=target,
                receipt=receipt,
                source_fingerprint_value=fingerprint_value,
                target_registry=target_registry,
                errors=errors,
            )
    if target_acceptance != set(required_acceptance_ids):
        errors.append("Requirement Verification targets must cover every required AC")
    if manifest.get("test_bindings") != expected_bindings:
        errors.append("Requirement Verification test_bindings must match canonical target nodes")
    if isinstance(fingerprint_value, str):
        validate_recorded_receipts(
            manifest=manifest,
            target_ids=target_ids,
            target_registry=target_registry,
            source_fingerprint_value=fingerprint_value,
            root=root,
            errors=errors,
            expected_verification_base_head=str(git_head),
        )
    return errors


def validate_traceability_results(
    *,
    trace_rows: list[list[str]],
    catalog_by_id: dict[str, dict[str, str]],
    scope_registry: dict[str, object],
    target_registry: dict[str, object],
    target_executor: TargetExecutor,
    verification_state: dict[str, object],
    root: Path,
    prior_result_lookup: Callable[[Path, str, str], str | None] = git_traceability_result,
    prior_attestation_lookup: Callable[[Path, str, str], str | None] = git_traceability_attestation,
    prior_attestation_hash_lookup: Callable[[Path, str, str], str | None] = git_file_sha256,
    prior_verification_state_lookup: Callable[
        [Path, str], dict[str, object] | None
    ] = git_verification_state,
    current_head_lookup: Callable[[Path], str | None] = repository_git_head,
) -> list[str]:
    errors: list[str] = []
    stage = verification_state.get("stage")
    change = verification_state.get("active_change")
    current_slice = verification_state.get("active_slice")
    result_update_authority = verification_state.get("result_update_authority")
    independent_evidence = verification_state.get("independent_requirement_verification_evidence")

    if verification_state.get("schema_version") != 2:
        errors.append("verification-state schema_version must equal 2")
    if stage not in ALLOWED_VERIFICATION_STAGES:
        errors.append(f"invalid verification stage: {stage}")
    if not isinstance(change, str) or not re.fullmatch(r"CHANGE-\d{3}", change):
        errors.append(f"invalid verification change: {change}")
    if not isinstance(current_slice, str) or not re.fullmatch(r"C\d{3}-S\d+", current_slice):
        errors.append(f"invalid verification slice: {current_slice}")
    if not isinstance(result_update_authority, str) or not re.fullmatch(
        r"C\d{3}-S\d+", result_update_authority
    ):
        errors.append(f"invalid result-update authority: {result_update_authority}")
    if isinstance(change, str) and isinstance(current_slice, str):
        expected_prefix = f"C{change.removeprefix('CHANGE-')}-S"
        if not current_slice.startswith(expected_prefix):
            errors.append(f"active slice/change mismatch: {change}/{current_slice}")
        if result_update_authority != current_slice:
            errors.append("result-update authority must equal the active slice")
        changes = scope_registry.get("changes")
        change_entry = changes.get(change) if isinstance(changes, dict) else None
        slices = change_entry.get("slices") if isinstance(change_entry, dict) else None
        if not isinstance(slices, dict) or current_slice not in slices:
            errors.append(f"active verification scope is unknown: {change}/{current_slice}")

    if stage == "REQUIREMENT_VERIFICATION":
        if (
            not isinstance(independent_evidence, list)
            or not independent_evidence
            or not all(isinstance(item, str) and item for item in independent_evidence)
        ):
            errors.append(
                "REQUIREMENT_VERIFICATION requires a non-empty list of independent "
                "Requirement Verification evidence manifests"
            )
        else:
            for reference in independent_evidence:
                repository_file(
                    root=root,
                    reference=reference,
                    label="independent Requirement Verification evidence",
                    errors=errors,
                    evidence_only=True,
                )

    for row in trace_rows:
        if len(row) != 8:
            continue
        requirement, _, _, _, implementation, test, evidence, result = row
        refs = evidence_paths(evidence)
        for reference in refs:
            repository_file(
                root=root,
                reference=reference,
                label=f"Traceability evidence for {requirement}",
                errors=errors,
            )

        if result == "IMPLEMENTED_UNVERIFIED":
            if "—" in {implementation, test, evidence}:
                errors.append(
                    f"IMPLEMENTED_UNVERIFIED lacks implementation/test/evidence: {requirement}"
                )
            for label, cell in (("implementation ref", implementation), ("test ref", test)):
                paths = evidence_paths(cell)
                if not paths:
                    errors.append(f"IMPLEMENTED_UNVERIFIED lacks {label}: {requirement}")
                for reference in paths:
                    repository_file(
                        root=root,
                        reference=reference,
                        label=f"{label} for {requirement}",
                        errors=errors,
                    )
            if len(refs) != 1:
                errors.append(
                    f"IMPLEMENTED_UNVERIFIED requires exactly one Implementation Attestation: "
                    f"{requirement}"
                )
            else:
                attestation_errors, attestation, _ = validate_implementation_attestation(
                    requirement=requirement,
                    attestation_reference=refs[0],
                    catalog_item=catalog_by_id.get(requirement),
                    scope_registry=scope_registry,
                    target_registry=target_registry,
                    target_executor=target_executor,
                    root=root,
                    expected_active_change=change,
                    expected_active_slice=current_slice,
                )
                errors.extend(attestation_errors)
                if attestation is not None:
                    if evidence_paths(implementation) != attestation.get("implementation_refs"):
                        errors.append(
                            "Traceability implementation refs must match "
                            "Implementation Attestation: "
                            f"{requirement}"
                        )
                    if evidence_paths(test) != attestation.get("test_refs"):
                        errors.append(
                            "Traceability test refs must match Implementation Attestation: "
                            f"{requirement}"
                        )

        if result != "PASS":
            continue
        if stage != "REQUIREMENT_VERIFICATION" or current_slice != result_update_authority:
            errors.append(
                "PASS is forbidden before the authorized independent Requirement "
                f"Verification stage: {requirement}"
            )
        if "—" in {implementation, test, evidence}:
            errors.append(f"PASS lacks implementation/test/evidence: {requirement}")
        if len(refs) != 1:
            errors.append(f"PASS requires exactly one evidence manifest: {requirement}")

        catalog_item = catalog_by_id.get(requirement)
        scope_entry = _scope_entry(scope_registry, change, current_slice, requirement)
        if (
            catalog_item is not None
            and isinstance(change, str)
            and not _change_contains(catalog_item["change"], change)
        ):
            errors.append(
                "cross-Change Requirement marked PASS: "
                f"{requirement} targets {catalog_item['change']}, current change is {change}"
            )
        if scope_entry is None:
            errors.append(
                "Requirement is not authorized in active scope "
                f"{change}/{current_slice}: {requirement}"
            )
        elif scope_entry.get("coverage") != "FULL":
            errors.append(
                "Requirement PASS requires FULL active-scope coverage: "
                f"{requirement}={scope_entry.get('coverage')}"
            )
        if catalog_item is not None and scope_entry is not None and len(refs) == 1:
            if not isinstance(independent_evidence, list) or refs[0] not in independent_evidence:
                errors.append(
                    "PASS evidence must be listed in independent Requirement "
                    "Verification evidence: "
                    f"{requirement}"
                )
            errors.extend(
                validate_pass_manifest(
                    requirement=requirement,
                    evidence_reference=refs[0],
                    required_acceptance_ids=list(scope_entry.get("acceptance_ids", [])),
                    verification_state=verification_state,
                    catalog_item=catalog_item,
                    scope_registry=scope_registry,
                    target_registry=target_registry,
                    target_executor=target_executor,
                    root=root,
                    prior_result_lookup=prior_result_lookup,
                    prior_attestation_lookup=prior_attestation_lookup,
                    prior_attestation_hash_lookup=prior_attestation_hash_lookup,
                    prior_verification_state_lookup=prior_verification_state_lookup,
                    current_head_lookup=current_head_lookup,
                )
            )

    return errors


def write_traceability(catalog: list[dict[str, str]], ac_by_id: dict[str, dict[str, str]]) -> None:
    lines = [
        "# Traceability Matrix",
        "",
        (
            "This matrix is generated from the Requirement Index by "
            "`scripts/quality/check_quality_docs.py --write-traceability`. Each "
            "Requirement has exactly one row. UNIMPLEMENTED covers not-yet-built, "
            "partial, and non-FULL scope; a FULL-owned implementation becomes "
            "IMPLEMENTED_UNVERIFIED only with a freshly revalidated Implementation "
            "Attestation, structured test nodes, and successful canonical targets. PASS "
            "requires that same unchanged provenance plus Requirement Verification "
            "targets. Manifest command/exit/reviewer claims never grant authority; "
            "reviewer independence is process-level."
        ),
        "",
        (
            "Result enum: `UNIMPLEMENTED`, `IMPLEMENTED_UNVERIFIED`, `PASS`, "
            "`FAIL`, `BLOCKED`, `NOT_APPLICABLE`."
        ),
        "",
        (
            "Completion reports must separately show: (1) all Requirements, "
            "(2) mandatory `ATOMIC` Requirements, and (3) `ROLLUP`/`E2E` gates. "
            "Partial work never promotes a full Rollup/E2E Acceptance."
        ),
        "",
        (
            "| Requirement | Acceptance | OpenSpec Capability | Change | "
            "Implementation | Test | Evidence | Result |"
        ),
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
            f"| {item['id']} | {acceptance} | UNASSIGNED | {item['change']} | — | "
            f"{verification} | — | UNIMPLEMENTED |"
        )
    lines.extend(
        [
            "",
            "## Update rule",
            "",
            (
                "When a Change begins, replace `UNASSIGNED` only with an actual "
                "OpenSpec capability identifier. Record concrete implementation/test/"
                "evidence references, then change Result only from executed evidence. "
                "Real external dependencies not exercised remain `BLOCKED` or "
                "`IMPLEMENTED_UNVERIFIED`, never PASS."
            ),
            "",
        ]
    )
    TRACE_PATH.write_text("\n".join(lines), encoding="utf-8")


def validate(
    catalog: list[dict[str, str]],
    contracts: list[dict[str, str]],
    scope_registry: dict[str, object],
    verification_state: dict[str, object],
    target_registry: dict[str, object],
    target_executor: TargetExecutor,
) -> list[str]:
    errors: list[str] = []
    req_ids = [item["id"] for item in catalog]
    req_set = set(req_ids)
    ac_ids = [item["id"] for item in contracts]
    ac_set = set(ac_ids)
    ac_by_id = {item["id"]: item for item in contracts}
    catalog_by_id = {item["id"]: item for item in catalog}
    unique(req_ids, "Requirement IDs", errors)
    unique(ac_ids, "Acceptance IDs", errors)
    errors.extend(
        validate_scope_registry(
            registry=scope_registry,
            catalog_by_id=catalog_by_id,
            acceptance_by_id=ac_by_id,
            root=ROOT,
        )
    )
    errors.extend(
        validate_verification_target_registry(
            registry=target_registry,
            catalog_by_id=catalog_by_id,
            acceptance_by_id=ac_by_id,
            scope_registry=scope_registry,
            root=ROOT,
            active_change=verification_state.get("active_change")
            if isinstance(verification_state.get("active_change"), str)
            else None,
            active_slice=verification_state.get("active_slice")
            if isinstance(verification_state.get("active_slice"), str)
            else None,
        )
    )

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
                errors.append(
                    "mandatory Requirement references missing AC: "
                    f"{item['id']}->{item['acceptance']}"
                )
        elif item["acceptance"] != "No":
            errors.append(f"SHOULD/MAY incorrectly made acceptance-required: {item['id']}")

    for contract in contracts:
        for req_id in REQ_ID_RE.findall(contract["requirement"]):
            if req_id not in req_set:
                errors.append(
                    f"Acceptance references missing Requirement: {contract['id']}->{req_id}"
                )
    catalog_ac_set = {item["acceptance"] for item in catalog if item["acceptance"] != "No"}
    requirement_ac_set = {item for item in ac_set if not item.startswith("REDLINE-AC-")}
    orphan_requirement_acs = sorted(requirement_ac_set - catalog_ac_set)
    if orphan_requirement_acs:
        errors.append(
            f"Requirement Acceptance not referenced by Catalog: {', '.join(orphan_requirement_acs)}"
        )

    redlines = sorted(item for item in ac_ids if item.startswith("REDLINE-AC-"))
    expected_redlines = [f"REDLINE-AC-{number:03d}" for number in range(1, 16)]
    if redlines != expected_redlines:
        errors.append("red-line set is not exactly REDLINE-AC-001..015")

    allowed_results = {
        "UNIMPLEMENTED",
        "IMPLEMENTED_UNVERIFIED",
        "PASS",
        "FAIL",
        "BLOCKED",
        "NOT_APPLICABLE",
    }
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
                errors.append(
                    f"Traceability AC mismatch: {requirement}->{acceptance}, expected {expected_ac}"
                )
            if expected_ac == "No" and not acceptance.startswith("—"):
                errors.append(
                    f"optional Traceability row should not claim AC: {requirement}->{acceptance}"
                )
        if result not in allowed_results:
            errors.append(f"invalid Traceability Result: {requirement}={result}")
    errors.extend(
        validate_traceability_results(
            trace_rows=trace_rows,
            catalog_by_id=catalog_by_id,
            scope_registry=scope_registry,
            target_registry=target_registry,
            target_executor=target_executor,
            verification_state=verification_state,
            root=ROOT,
        )
    )
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
        elif (
            reference.startswith("AC-") or reference.startswith("REDLINE-AC-")
        ) and reference not in ac_set:
            errors.append(f"PLAN references missing Acceptance: {reference}")

    slice_section = plan_text.split("## CHANGE-001 reviewable slices", 1)[-1].split(
        "### Recommended execution order", 1
    )[0]
    slice_refs = expand_ranges(slice_section)
    for item in catalog:
        if item["id"] not in slice_refs:
            continue
        cross_change_gate = item["kind"] in {"ROLLUP", "E2E"} and item["change"] != "CHANGE-001"
        if cross_change_gate:
            errors.append(
                f"cross-Change Rollup/E2E Requirement bound to CHANGE-001 Slice: {item['id']}"
            )
        if item["kind"] == "SCOPE_GUARD":
            errors.append(f"Scope Guard presented as CHANGE-001 Slice outcome: {item['id']}")

    req_by_id = {item["id"]: item for item in catalog}
    for row in rows(
        PLAN_PATH,
        ("| 1 | C001-", "| 2 | C001-", "| 3 | C001-", "| 4 | C001-", "| 5 | C001-", "| 6 | C001-"),
    ):
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
                cross_change_gate = (
                    item["kind"] in {"ROLLUP", "E2E"} and item["change"] != "CHANGE-001"
                )
                if cross_change_gate:
                    errors.append(f"cross-Change Rollup/E2E AC bound to CHANGE-001 Slice: {ac_id}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-traceability", action="store_true")
    args = parser.parse_args()
    catalog, _ = load_catalog()
    contracts, ac_by_id = load_acceptance()
    scope_registry = load_verification_scope()
    verification_state = load_verification_state()
    target_registry = load_target_registry(VERIFICATION_TARGETS_PATH)
    runtime = VerificationRuntime(root=ROOT, registry=target_registry)

    def target_executor(
        target_id: str, target: dict[str, object], fingerprint: str
    ) -> dict[str, object]:
        return runtime.execute(
            target_id=target_id,
            target=target,
            source_fingerprint=fingerprint,
        )

    if args.write_traceability:
        write_traceability(catalog, ac_by_id)
    errors = validate(
        catalog,
        contracts,
        scope_registry,
        verification_state,
        target_registry,
        target_executor,
    )
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
    print(f"verification_stage={verification_state['stage']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
