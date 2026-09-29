from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from scripts.quality.check_quality_docs import (
    ROOT,
    file_sha256,
    git_traceability_result,
    implementation_source_fingerprint,
    load_acceptance,
    load_catalog,
    load_verification_scope,
    validate_execution_receipt,
    validate_scope_registry,
    validate_traceability_results,
    validate_verification_target_registry,
)
from scripts.quality.verification_runner import (
    VerificationRuntime,
    canonical_hash,
)
from scripts.quality.verification_runner import (
    load_target_registry as load_canonical_target_registry,
)

pytestmark = pytest.mark.unit


def catalog(
    *,
    requirement: str = "REQ-TEST-001",
    change: str = "CHANGE-001",
    kind: str = "ATOMIC",
    acceptance: str = "AC-TEST-001",
) -> dict[str, dict[str, str]]:
    return {
        requirement: {
            "id": requirement,
            "kind": kind,
            "change": change,
            "acceptance": acceptance,
        }
    }


def scope_registry(
    *,
    requirement: str = "REQ-TEST-001",
    owner_slice: str = "C001-S1",
    coverage: str = "FULL",
    acceptance_ids: list[str] | None = None,
    include_requirement: bool = True,
) -> dict[str, object]:
    slices: dict[str, object] = {
        "C001-S1": {"requirements": {}},
        "C001-S2": {"requirements": {}},
    }
    if include_requirement:
        requirements = slices[owner_slice]["requirements"]
        assert isinstance(requirements, dict)
        requirements[requirement] = {
            "coverage": coverage,
            "acceptance_ids": acceptance_ids or ["AC-TEST-001"],
        }
    return {"schema_version": 1, "changes": {"CHANGE-001": {"slices": slices}}}


def trace_row(
    *,
    result: str,
    evidence: str,
    requirement: str = "REQ-TEST-001",
    acceptance: str = "AC-TEST-001",
) -> list[str]:
    return [
        requirement,
        acceptance,
        "test-capability",
        "CHANGE-001",
        "`src/implementation.py`",
        "`tests/test_implementation.py`",
        f"`{evidence}`",
        result,
    ]


def state(
    *,
    stage: str,
    independent_evidence: str | None = None,
    active_change: str = "CHANGE-001",
    active_slice: str = "C001-S1",
    result_update_authority: str | None = None,
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "active_change": active_change,
        "active_slice": active_slice,
        "result_update_authority": result_update_authority or active_slice,
        "stage": stage,
        "independent_requirement_verification_evidence": (
            [independent_evidence] if independent_evidence is not None else None
        ),
    }


def prepare_sources(root: Path) -> None:
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "src/implementation.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "tests/test_implementation.py").write_text(
        "import pytest\n\n"
        '@pytest.mark.quality_binding("REQ-TEST-001", "AC-TEST-001")\n'
        "def test_value():\n    assert True\n",
        encoding="utf-8",
    )


def target_registry(
    *,
    requirement: str = "REQ-TEST-001",
    acceptance_ids: list[str] | None = None,
    change_id: str = "CHANGE-001",
    slice_id: str = "C001-S1",
) -> dict[str, object]:
    acceptance_ids = ["AC-TEST-001"] if acceptance_ids is None else acceptance_ids
    node = "tests/test_implementation.py::test_value"

    def target(stage: str, receipt: str) -> dict[str, object]:
        return {
            "requirement_id": requirement,
            "acceptance_ids": acceptance_ids,
            "change_id": change_id,
            "slice_id": slice_id,
            "verification_stage": stage,
            "verification_level": "INTEGRATION",
            "runner": "pytest",
            "setup": "none",
            "working_directory": ".",
            "arguments": [node],
            "test_nodes": [
                {
                    "nodeid": node,
                    "requirement_id": requirement,
                    "acceptance_ids": acceptance_ids,
                }
            ],
            "receipt_path": receipt,
        }

    return {
        "schema_version": 1,
        "targets": {
            "VT-TEST-IMPLEMENTATION": target(
                "IMPLEMENTATION", "docs/quality/evidence/receipts/implementation.json"
            ),
            "VT-TEST-RV": target(
                "REQUIREMENT_VERIFICATION", "docs/quality/evidence/receipts/rv.json"
            ),
        },
    }


def fake_receipt(
    registry: dict[str, object], target_id: str, source_fingerprint_value: str
) -> dict[str, object]:
    targets = registry["targets"]
    assert isinstance(targets, dict)
    target = targets[target_id]
    assert isinstance(target, dict)
    nodeids = list(target["arguments"])
    bindings: list[dict[str, object]] = []
    for candidate in targets.values():
        assert isinstance(candidate, dict)
        for node in candidate["test_nodes"]:
            if node["nodeid"] in nodeids:
                binding = {
                    "nodeid": node["nodeid"],
                    "requirement_id": node["requirement_id"],
                    "acceptance_ids": node["acceptance_ids"],
                }
                if binding not in bindings:
                    bindings.append(binding)
    return {
        "schema_version": 2,
        "receipt_id": "runner-created",
        "target_id": target_id,
        "requirement_id": target["requirement_id"],
        "acceptance_ids": target["acceptance_ids"],
        "verification_stage": target["verification_stage"],
        "verification_level": target["verification_level"],
        "verification_base_head": "a" * 40,
        "target_registry_hash": canonical_hash(registry),
        "target_definition_hash": canonical_hash(target),
        "source_fingerprint": source_fingerprint_value,
        "collection_exit_code": 0,
        "collected_nodes": nodeids,
        "collected_bindings": bindings,
        "exact_executable_argv": ["uv", "run", "pytest", *nodeids],
        "started_at": "2026-09-28T00:00:00Z",
        "finished_at": "2026-09-28T00:00:01Z",
        "executed_at": "2026-09-28T00:00:01Z",
        "actual_exit_code": 0,
        "test_results": {nodeid: "passed" for nodeid in nodeids},
        "stdout_sha256": "stdout-hash",
        "stderr_sha256": "stderr-hash",
        "working_directory": ".",
    }


def write_receipt(
    root: Path,
    registry: dict[str, object],
    target_id: str,
    source_fingerprint_value: str,
) -> dict[str, str]:
    targets = registry["targets"]
    assert isinstance(targets, dict)
    target = targets[target_id]
    assert isinstance(target, dict)
    reference = target["receipt_path"]
    assert isinstance(reference, str)
    path = root / reference
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(fake_receipt(registry, target_id, source_fingerprint_value)),
        encoding="utf-8",
    )
    return {"target_id": target_id, "receipt_ref": reference, "receipt_hash": file_sha256(path)}


def valid_attestation(
    root: Path,
    *,
    path: str = "docs/quality/evidence/change-001/c001-s1/implementation/req-test-001.json",
    requirement: str = "REQ-TEST-001",
    acceptance_ids: list[str] | None = None,
    change_id: str = "CHANGE-001",
    slice_id: str = "C001-S1",
    implementation_refs: list[str] | None = None,
    test_refs: list[str] | None = None,
) -> str:
    prepare_sources(root)
    required_acceptance_ids = ["AC-TEST-001"] if acceptance_ids is None else acceptance_ids
    implementation_refs = implementation_refs or ["src/implementation.py"]
    test_refs = test_refs or ["tests/test_implementation.py"]
    references = implementation_refs + test_refs
    fingerprint = implementation_source_fingerprint(
        root,
        requirement=requirement,
        change_id=change_id,
        slice_id=slice_id,
        references=references,
    )
    registry = target_registry(
        requirement=requirement,
        acceptance_ids=required_acceptance_ids,
        change_id=change_id,
        slice_id=slice_id,
    )
    manifest = {
        "schema_version": 2,
        "requirement_id": requirement,
        "change_id": change_id,
        "slice_id": slice_id,
        "coverage": "FULL",
        "implementation_stage": "IMPLEMENTATION",
        "implementation_refs": implementation_refs,
        "test_refs": test_refs,
        "test_bindings": [
            {
                "target_id": "VT-TEST-IMPLEMENTATION",
                "test_nodeid": "tests/test_implementation.py::test_value",
                "requirement_id": requirement,
                "acceptance_ids": required_acceptance_ids,
            }
        ],
        "required_acceptance_ids": required_acceptance_ids,
        "verification_targets": ["VT-TEST-IMPLEMENTATION"],
        "execution_receipts": [
            write_receipt(root, registry, "VT-TEST-IMPLEMENTATION", fingerprint)
        ],
        "source_fingerprint": fingerprint,
        "created_at": "2026-09-28T00:00:00Z",
    }
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def valid_manifest(
    root: Path,
    *,
    path: str = "docs/quality/evidence/req-test-001.json",
    requirement: str = "REQ-TEST-001",
    acceptance_ids: list[str] | None = None,
    change_id: str = "CHANGE-001",
    slice_id: str = "C001-S1",
) -> str:
    required_acceptance_ids = ["AC-TEST-001"] if acceptance_ids is None else acceptance_ids
    attestation_reference = valid_attestation(
        root,
        requirement=requirement,
        acceptance_ids=required_acceptance_ids,
        change_id=change_id,
        slice_id=slice_id,
    )
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    references = ["src/implementation.py", "tests/test_implementation.py"]
    fingerprint = implementation_source_fingerprint(
        root,
        requirement=requirement,
        change_id=change_id,
        slice_id=slice_id,
        references=references,
    )
    registry = target_registry(
        requirement=requirement,
        acceptance_ids=required_acceptance_ids,
        change_id=change_id,
        slice_id=slice_id,
    )
    manifest = {
        "schema_version": 2,
        "requirement_id": requirement,
        "acceptance_ids": required_acceptance_ids,
        "change_id": change_id,
        "slice_id": slice_id,
        "verification_stage": "REQUIREMENT_VERIFICATION",
        "result": "PASS",
        "verified_at": "2026-09-28T00:00:00Z",
        "git_head": "a" * 40,
        "implementation_refs": [references[0]],
        "test_refs": [references[1]],
        "verification_targets": ["VT-TEST-RV"],
        "test_bindings": [
            {
                "target_id": "VT-TEST-RV",
                "test_nodeid": "tests/test_implementation.py::test_value",
                "requirement_id": requirement,
                "acceptance_ids": required_acceptance_ids,
            }
        ],
        "execution_receipts": [write_receipt(root, registry, "VT-TEST-RV", fingerprint)],
        "artifacts": [references[1]],
        "reviewer_gate": "PASS",
        "source_fingerprint": fingerprint,
        "implementation_attestation_ref": attestation_reference,
        "implementation_attestation_hash": file_sha256(root / attestation_reference),
    }
    target.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def validate(
    root: Path,
    *,
    stage: str,
    result: str,
    evidence: str,
    requirement: str = "REQ-TEST-001",
    acceptance: str = "AC-TEST-001",
    catalog_change: str = "CHANGE-001",
    registry: dict[str, object] | None = None,
    independent_evidence: str | None = None,
    active_change: str = "CHANGE-001",
    active_slice: str = "C001-S1",
    prior_result: str | None = None,
    prior_attestation: str | None = None,
    prior_active_slice: str | None = None,
    target_registry_override: dict[str, object] | None = None,
    target_executor_override=None,
) -> list[str]:
    if prior_result is None:
        prior_result = "IMPLEMENTED_UNVERIFIED" if result == "PASS" else "UNIMPLEMENTED"
    if prior_attestation is None and result == "PASS":
        try:
            manifest = json.loads((root / evidence).read_text(encoding="utf-8"))
            prior_attestation = manifest.get("implementation_attestation_ref")
        except (OSError, json.JSONDecodeError):
            prior_attestation = None
    targets = target_registry_override or target_registry(
        requirement=requirement,
        acceptance_ids=[acceptance],
        change_id=active_change,
        slice_id=active_slice,
    )
    executor = target_executor_override or (
        lambda target_id, _target, fingerprint: fake_receipt(targets, target_id, fingerprint)
    )
    return validate_traceability_results(
        trace_rows=[
            trace_row(
                result=result,
                evidence=evidence,
                requirement=requirement,
                acceptance=acceptance,
            )
        ],
        catalog_by_id=catalog(requirement=requirement, change=catalog_change),
        scope_registry=registry
        or scope_registry(requirement=requirement, acceptance_ids=[acceptance]),
        target_registry=targets,
        target_executor=executor,
        verification_state=state(
            stage=stage,
            independent_evidence=independent_evidence,
            active_change=active_change,
            active_slice=active_slice,
        ),
        root=root,
        prior_result_lookup=lambda _root, _head, _requirement: prior_result,
        prior_attestation_lookup=lambda _root, _head, _requirement: prior_attestation,
        prior_attestation_hash_lookup=lambda _root, _head, reference: (
            file_sha256(root / reference) if (root / reference).is_file() else None
        ),
        prior_verification_state_lookup=lambda _root, _head: state(
            stage="CODE_REVIEW_READY",
            active_change=active_change,
            active_slice=prior_active_slice or active_slice,
        ),
        current_head_lookup=lambda _root: "a" * 40,
    )


def test_scope_registry_matches_canonical_quality_sources() -> None:
    requirements, catalog_by_id = load_catalog()
    contracts, acceptance_by_id = load_acceptance()
    assert requirements
    assert contracts
    errors = validate_scope_registry(
        registry=load_verification_scope(),
        catalog_by_id=catalog_by_id,
        acceptance_by_id=acceptance_by_id,
        root=ROOT,
    )
    assert errors == []


def test_current_s1_full_requirements_remain_implemented_unverified() -> None:
    expected = {
        "REQ-ARCH-002",
        "REQ-ARCH-010",
        "REQ-ARCH-013",
        "REQ-GOVERNANCE-011",
        "REQ-FOUNDATION-001",
    }
    registry = load_verification_scope()
    requirements = registry["changes"]["CHANGE-001"]["slices"]["C001-S1"]["requirements"]
    assert {
        requirement for requirement, entry in requirements.items() if entry["coverage"] == "FULL"
    } == expected

    results: dict[str, str] = {}
    for line in (ROOT / "docs/quality/TRACEABILITY.md").read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 8 and cells[0] in expected:
            results[cells[0]] = cells[-1]
    assert results == {requirement: "IMPLEMENTED_UNVERIFIED" for requirement in expected}


def validate_current_target_registry(registry: dict[str, object]) -> list[str]:
    _, catalog_by_id = load_catalog()
    _, acceptance_by_id = load_acceptance()
    return validate_verification_target_registry(
        registry=registry,
        catalog_by_id=catalog_by_id,
        acceptance_by_id=acceptance_by_id,
        scope_registry=load_verification_scope(),
        root=ROOT,
        active_change="CHANGE-001",
        active_slice="C001-S1",
    )


def test_rv_target_001_every_s1_full_requirement_has_canonical_target() -> None:
    registry = load_canonical_target_registry()
    assert validate_current_target_registry(registry) == []
    targets = registry["targets"]
    full_requirements = {
        requirement
        for requirement, entry in load_verification_scope()["changes"]["CHANGE-001"]["slices"][
            "C001-S1"
        ]["requirements"].items()
        if entry["coverage"] == "FULL"
    }
    rv_requirements = {
        target["requirement_id"]
        for target in targets.values()
        if target["verification_stage"] == "REQUIREMENT_VERIFICATION"
    }
    assert rv_requirements == full_requirements


def test_rv_target_002_all_mandatory_acceptance_is_covered() -> None:
    registry = copy.deepcopy(load_canonical_target_registry())
    del registry["targets"]["VT-RV-S1-FOUNDATION-001"]
    errors = validate_current_target_registry(registry)
    assert any(
        "FULL Requirement lacks canonical REQUIREMENT_VERIFICATION target: "
        "REQ-FOUNDATION-001" in error
        for error in errors
    )


def test_rv_target_003_requirement_ownership_is_enforced() -> None:
    registry = copy.deepcopy(load_canonical_target_registry())
    registry["targets"]["VT-RV-S1-ARCH-010"]["slice_id"] = "C001-S2"
    errors = validate_current_target_registry(registry)
    assert any("does not match canonical FULL owner" in error for error in errors)


def test_rv_target_004_acceptance_ownership_is_enforced() -> None:
    registry = copy.deepcopy(load_canonical_target_registry())
    target = registry["targets"]["VT-RV-S1-GOVERNANCE-011"]
    target["acceptance_ids"] = ["AC-FOUNDATION-001"]
    target["test_nodes"][0]["acceptance_ids"] = ["AC-FOUNDATION-001"]
    errors = validate_current_target_registry(registry)
    assert any("Acceptance ownership mismatch" in error for error in errors)
    assert any("AC does not belong" in error for error in errors)


def test_rv_target_005_stage_is_requirement_verification() -> None:
    registry = copy.deepcopy(load_canonical_target_registry())
    registry["targets"]["VT-RV-S1-ARCH-013"]["verification_stage"] = "IMPLEMENTATION"
    errors = validate_current_target_registry(registry)
    assert any(
        "FULL Requirement lacks canonical REQUIREMENT_VERIFICATION target: REQ-ARCH-013" in error
        for error in errors
    )


def test_registry_cannot_self_authorize_s2_requirement_for_s1() -> None:
    _, catalog_by_id = load_catalog()
    _, acceptance_by_id = load_acceptance()
    registry = copy.deepcopy(load_verification_scope())
    registry["changes"]["CHANGE-001"]["slices"]["C001-S1"]["requirements"]["REQ-DATA-001"][
        "coverage"
    ] = "FULL"
    errors = validate_scope_registry(
        registry=registry,
        catalog_by_id=catalog_by_id,
        acceptance_by_id=acceptance_by_id,
        root=ROOT,
    )
    assert any("absent from C001-S1 tasks" in error for error in errors)


def test_registry_rejects_wrong_acceptance_ownership() -> None:
    _, catalog_by_id = load_catalog()
    _, acceptance_by_id = load_acceptance()
    registry = copy.deepcopy(load_verification_scope())
    registry["changes"]["CHANGE-001"]["slices"]["C001-S1"]["requirements"]["REQ-FOUNDATION-001"][
        "acceptance_ids"
    ] = ["AC-DATA-001"]
    errors = validate_scope_registry(
        registry=registry,
        catalog_by_id=catalog_by_id,
        acceptance_by_id=acceptance_by_id,
        root=ROOT,
    )
    assert any("Acceptance ownership drift" in error for error in errors)


def test_registry_rejects_partial_requirement_promoted_to_full() -> None:
    _, catalog_by_id = load_catalog()
    _, acceptance_by_id = load_acceptance()
    registry = copy.deepcopy(load_verification_scope())
    registry["changes"]["CHANGE-001"]["slices"]["C001-S1"]["requirements"]["REQ-ARCH-001"][
        "coverage"
    ] = "FULL"
    errors = validate_scope_registry(
        registry=registry,
        catalog_by_id=catalog_by_id,
        acceptance_by_id=acceptance_by_id,
        root=ROOT,
    )
    assert any("canonical partial Requirement" in error for error in errors)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda value: value.pop("active_change"), "invalid verification change"),
        (lambda value: value.pop("active_slice"), "invalid verification slice"),
        (
            lambda value: value.update(active_slice="C001-S9", result_update_authority="C001-S9"),
            "active verification scope is unknown",
        ),
        (
            lambda value: value.update(active_slice="C002-S1", result_update_authority="C002-S1"),
            "active slice/change mismatch",
        ),
    ],
)
def test_active_scope_metadata_fails_closed(mutation, expected: str) -> None:
    metadata = state(stage="CODE_REVIEW_READY")
    mutation(metadata)
    targets = target_registry()
    errors = validate_traceability_results(
        trace_rows=[],
        catalog_by_id=catalog(),
        scope_registry=scope_registry(),
        target_registry=targets,
        target_executor=lambda target_id, _target, fingerprint: fake_receipt(
            targets, target_id, fingerprint
        ),
        verification_state=metadata,
        root=ROOT,
    )
    assert any(expected in error for error in errors)


def test_implementation_and_code_review_stages_reject_pass(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    for stage in ("IMPLEMENTATION", "CODE_REVIEW_READY"):
        errors = validate(tmp_path, stage=stage, result="PASS", evidence=evidence)
        assert any("PASS is forbidden" in error for error in errors)


def test_qg_001_external_evidence_fails(tmp_path: Path) -> None:
    prepare_sources(tmp_path)
    evidence = "/tmp/external-evidence.json"
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("repository-relative" in error for error in errors)


def test_qg_002_empty_evidence_fails(tmp_path: Path) -> None:
    prepare_sources(tmp_path)
    evidence = "docs/quality/evidence/empty.json"
    path = tmp_path / evidence
    path.parent.mkdir(parents=True)
    path.touch()
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("is empty" in error for error in errors)


def test_qg_003_arbitrary_file_fails(tmp_path: Path) -> None:
    prepare_sources(tmp_path)
    evidence = "docs/quality/evidence/README.md"
    path = tmp_path / evidence
    path.parent.mkdir(parents=True)
    path.write_text("not verification evidence", encoding="utf-8")
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("not valid JSON" in error for error in errors)


def test_qg_004_symlink_escape_fails(tmp_path: Path) -> None:
    prepare_sources(tmp_path)
    outside = tmp_path.parent / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    evidence = "docs/quality/evidence/link.json"
    link = tmp_path / evidence
    link.parent.mkdir(parents=True)
    link.symlink_to(outside)
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("escapes repository root" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "missing", "expected"),
    [
        ("implementation_refs", "src/missing.py", "implementation ref does not exist"),
        ("test_refs", "tests/missing.py", "test ref does not exist"),
    ],
)
def test_qg_005_006_nonexistent_source_ref_fails(
    tmp_path: Path, field: str, missing: str, expected: str
) -> None:
    evidence = valid_manifest(tmp_path)
    path = tmp_path / evidence
    manifest = json.loads(path.read_text())
    manifest[field] = [missing]
    path.write_text(json.dumps(manifest))
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any(expected in error for error in errors)


def test_qg_007_stale_fingerprint_fails(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    (tmp_path / "src/implementation.py").write_text("VALUE = 2\n")
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("source_fingerprint" in error for error in errors)


def test_qg_008_fake_stage_without_manifest_fails(tmp_path: Path) -> None:
    prepare_sources(tmp_path)
    evidence = "docs/quality/evidence/missing.json"
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("does not exist" in error for error in errors)


def test_qg_009_implemented_unverified_is_allowed(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path)
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
    )
    assert errors == []


def test_qg_010_valid_requirement_verification_manifest_allows_pass(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert errors == []


def test_direct_unimplemented_to_pass_transition_fails(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
        prior_result="UNIMPLEMENTED",
    )
    assert any("IMPLEMENTED_UNVERIFIED" in error for error in errors)


def test_manifest_git_head_must_equal_repository_head(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    path = tmp_path / evidence
    manifest = json.loads(path.read_text())
    manifest["git_head"] = "b" * 40
    path.write_text(json.dumps(manifest))
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("must equal repository HEAD" in error for error in errors)


def test_git_head_binds_pass_to_implemented_unverified_prestate(tmp_path: Path) -> None:
    traceability = tmp_path / "docs/quality/TRACEABILITY.md"
    traceability.parent.mkdir(parents=True)
    traceability.write_text(
        "| REQ-TEST-001 | AC-TEST-001 | capability | CHANGE-001 | impl | test | "
        "evidence | IMPLEMENTED_UNVERIFIED |\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "docs/quality/TRACEABILITY.md"], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=NeedRadar Test",
            "-c",
            "user.email=needradar-test@example.invalid",
            "commit",
            "-qm",
            "quality prestate",
        ],
        cwd=tmp_path,
        check=True,
    )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert git_traceability_result(tmp_path, head, "REQ-TEST-001") == "IMPLEMENTED_UNVERIFIED"


def test_qg_scope_001_s1_evidence_cannot_pass_s2_requirement(tmp_path: Path) -> None:
    requirement = "REQ-DATA-001"
    evidence = valid_manifest(tmp_path)
    manifest_path = tmp_path / evidence
    manifest = json.loads(manifest_path.read_text())
    manifest["requirement_id"] = requirement
    manifest["acceptance_ids"] = ["AC-DATA-001"]
    manifest_path.write_text(json.dumps(manifest))
    registry = scope_registry(
        requirement=requirement,
        owner_slice="C001-S1",
        coverage="DEFERRED",
        acceptance_ids=["AC-DATA-001"],
    )
    registry["changes"]["CHANGE-001"]["slices"]["C001-S2"]["requirements"][requirement] = {
        "coverage": "FULL",
        "acceptance_ids": ["AC-DATA-001"],
    }
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        requirement=requirement,
        acceptance="AC-DATA-001",
        registry=registry,
        independent_evidence=evidence,
    )
    assert any("requires FULL" in error for error in errors)


def test_qg_scope_002_s1_evidence_cannot_pass_change_002_requirement(tmp_path: Path) -> None:
    requirement = "REQ-PLANNER-001"
    evidence = valid_manifest(
        tmp_path,
        requirement=requirement,
        acceptance_ids=["AC-PLANNER-001"],
    )
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        requirement=requirement,
        acceptance="AC-PLANNER-001",
        catalog_change="CHANGE-002",
        registry=scope_registry(requirement=requirement, include_requirement=False),
        independent_evidence=evidence,
    )
    assert any("cross-Change Requirement" in error for error in errors)


def test_qg_scope_003_correct_requirement_with_wrong_slice_fails(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path, slice_id="C001-S2")
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        registry=scope_registry(owner_slice="C001-S1"),
        independent_evidence=evidence,
        active_slice="C001-S2",
    )
    assert any("not authorized in active scope" in error for error in errors)


def test_qg_scope_004_partial_requirement_cannot_pass(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        registry=scope_registry(coverage="PARTIAL"),
        independent_evidence=evidence,
    )
    assert any("requires FULL" in error for error in errors)


def test_qg_scope_005_unrelated_acceptance_fails(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path, acceptance_ids=["AC-OTHER-001"])
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("acceptance_ids must equal" in error for error in errors)


def test_qg_scope_006_missing_required_acceptance_fails(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    path = tmp_path / evidence
    manifest = json.loads(path.read_text())
    manifest["acceptance_ids"] = []
    path.write_text(json.dumps(manifest))
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("acceptance_ids must equal" in error for error in errors)


def deferred_s1_full_s2_registry(
    *, requirement: str = "REQ-DATA-001", acceptance: str = "AC-DATA-001"
) -> dict[str, object]:
    registry = scope_registry(
        requirement=requirement,
        owner_slice="C001-S1",
        coverage="DEFERRED",
        acceptance_ids=[acceptance],
    )
    registry["changes"]["CHANGE-001"]["slices"]["C001-S2"]["requirements"][requirement] = {
        "coverage": "FULL",
        "acceptance_ids": [acceptance],
    }
    return registry


def test_qg_iu_001_s1_deferred_requirement_cannot_enter_iu(tmp_path: Path) -> None:
    requirement = "REQ-DATA-001"
    evidence = valid_attestation(
        tmp_path,
        requirement=requirement,
        acceptance_ids=["AC-DATA-001"],
        slice_id="C001-S1",
    )
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        requirement=requirement,
        acceptance="AC-DATA-001",
        registry=deferred_s1_full_s2_registry(),
    )
    assert any("canonical FULL owner in active Slice" in error for error in errors)


def test_qg_iu_002_forged_persisted_iu_without_attestation_fails(tmp_path: Path) -> None:
    prepare_sources(tmp_path)
    evidence = "docs/quality/evidence/change-001/c001-s1/code-review.md"
    path = tmp_path / evidence
    path.parent.mkdir(parents=True)
    path.write_text("not an Implementation Attestation", encoding="utf-8")
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        prior_result="IMPLEMENTED_UNVERIFIED",
    )
    assert any("Implementation Attestation" in error for error in errors)


def test_qg_iu_003_wrong_slice_attestation_fails(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path, slice_id="C001-S2")
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
    )
    assert any("slice_id must equal 'C001-S1'" in error for error in errors)


def test_qg_iu_004_s2_requirement_cannot_reuse_s1_test_refs(tmp_path: Path) -> None:
    requirement = "REQ-DATA-001"
    evidence = valid_attestation(
        tmp_path,
        requirement=requirement,
        acceptance_ids=["AC-DATA-001"],
        slice_id="C001-S2",
    )
    test_path = tmp_path / "tests/test_implementation.py"
    test_path.write_text("# REQ-FOUNDATION-001 AC-FOUNDATION-001\ndef test_value(): pass\n")
    attestation_path = tmp_path / evidence
    attestation = json.loads(attestation_path.read_text())
    attestation["source_fingerprint"] = implementation_source_fingerprint(
        tmp_path,
        requirement=requirement,
        change_id="CHANGE-001",
        slice_id="C001-S2",
        references=attestation["implementation_refs"] + attestation["test_refs"],
    )
    attestation_path.write_text(json.dumps(attestation))
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        requirement=requirement,
        acceptance="AC-DATA-001",
        registry=deferred_s1_full_s2_registry(),
        active_slice="C001-S2",
    )
    assert any("execution receipt source fingerprint is stale" in error for error in errors)


@pytest.mark.parametrize("coverage", ["PARTIAL", "DEFERRED"])
def test_qg_iu_005_006_non_full_requirement_cannot_enter_iu(tmp_path: Path, coverage: str) -> None:
    evidence = valid_attestation(tmp_path)
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        registry=scope_registry(coverage=coverage),
    )
    assert any("exactly one canonical FULL owner" in error for error in errors)


def test_qg_iu_007_cross_change_requirement_cannot_enter_iu(tmp_path: Path) -> None:
    requirement = "REQ-PLANNER-001"
    acceptance = "AC-PLANNER-001"
    evidence = valid_attestation(
        tmp_path,
        requirement=requirement,
        acceptance_ids=[acceptance],
        change_id="CHANGE-002",
        slice_id="C002-S1",
    )
    registry = {
        "schema_version": 1,
        "changes": {
            "CHANGE-001": {"slices": {"C001-S1": {"requirements": {}}}},
            "CHANGE-002": {
                "slices": {
                    "C002-S1": {
                        "requirements": {
                            requirement: {
                                "coverage": "FULL",
                                "acceptance_ids": [acceptance],
                            }
                        }
                    }
                }
            },
        },
    }
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        requirement=requirement,
        acceptance=acceptance,
        catalog_change="CHANGE-002",
        registry=registry,
    )
    assert any("canonical owner in active Change" in error for error in errors)


def test_qg_iu_008_valid_s1_full_requirement_can_enter_iu(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path)
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
    )
    assert errors == []


def test_qg_iu_009_pass_rejects_different_attestation_than_prestate(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    manifest_path = tmp_path / evidence
    manifest = json.loads(manifest_path.read_text())
    recorded_attestation = manifest["implementation_attestation_ref"]
    other_attestation = valid_attestation(
        tmp_path,
        path="docs/quality/evidence/change-001/c001-s1/implementation/other.json",
    )
    manifest["implementation_attestation_ref"] = other_attestation
    manifest["implementation_attestation_hash"] = file_sha256(tmp_path / other_attestation)
    manifest_path.write_text(json.dumps(manifest))
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
        prior_attestation=recorded_attestation,
    )
    assert any("recorded by the IMPLEMENTED_UNVERIFIED pre-state" in error for error in errors)


def test_qg_iu_010_source_changed_after_attestation_blocks_pass(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    (tmp_path / "src/implementation.py").write_text("VALUE = 99\n")
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("current sources" in error for error in errors)


def test_qg_iu_011_matching_iu_and_independent_rv_allows_pass(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert errors == []


def test_reviewer_r4_two_stage_prestate_laundering_chain_is_blocked(tmp_path: Path) -> None:
    requirement = "REQ-DATA-001"
    acceptance = "AC-DATA-001"
    registry = deferred_s1_full_s2_registry(requirement=requirement, acceptance=acceptance)
    forged_s1_attestation = valid_attestation(
        tmp_path,
        path="docs/quality/evidence/change-001/c001-s1/implementation/req-data-001.json",
        requirement=requirement,
        acceptance_ids=[acceptance],
        slice_id="C001-S1",
    )
    iu_errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=forged_s1_attestation,
        requirement=requirement,
        acceptance=acceptance,
        registry=registry,
    )
    assert any("canonical FULL owner in active Slice" in error for error in iu_errors)

    rv_evidence = valid_manifest(
        tmp_path,
        requirement=requirement,
        acceptance_ids=[acceptance],
        slice_id="C001-S2",
    )
    rv_path = tmp_path / rv_evidence
    rv_manifest = json.loads(rv_path.read_text())
    rv_manifest["implementation_attestation_ref"] = forged_s1_attestation
    rv_manifest["implementation_attestation_hash"] = file_sha256(tmp_path / forged_s1_attestation)
    rv_path.write_text(json.dumps(rv_manifest))
    pass_errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=rv_evidence,
        requirement=requirement,
        acceptance=acceptance,
        registry=registry,
        independent_evidence=rv_evidence,
        active_slice="C001-S2",
        prior_result="IMPLEMENTED_UNVERIFIED",
        prior_attestation=forged_s1_attestation,
        prior_active_slice="C001-S1",
    )
    assert any("slice_id must equal 'C001-S2'" in error for error in pass_errors)


def test_r5_a01_forged_persisted_iu_fails(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path)
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        registry=scope_registry(coverage="DEFERRED"),
        prior_result="IMPLEMENTED_UNVERIFIED",
    )
    assert any("exactly one canonical FULL owner" in error for error in errors)


def test_r5_a02_persisted_iu_then_slice_switch_still_fails(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path, slice_id="C001-S1")
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        registry=scope_registry(owner_slice="C001-S2"),
        active_slice="C001-S2",
        prior_result="IMPLEMENTED_UNVERIFIED",
    )
    assert any("slice_id must equal 'C001-S2'" in error for error in errors)


def _failed_executor(registry: dict[str, object]):
    def execute(target_id: str, _target: dict[str, object], fingerprint: str):
        receipt = fake_receipt(registry, target_id, fingerprint)
        receipt["actual_exit_code"] = 1
        receipt["test_results"] = {nodeid: "failed" for nodeid in receipt["collected_nodes"]}
        return receipt

    return execute


def test_r5_a03_nonexistent_claimed_command_cannot_authorize(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path)
    manifest_path = tmp_path / evidence
    manifest = json.loads(manifest_path.read_text())
    manifest["verification_commands"] = [{"command": "does-not-exist", "exit_code": 0}]
    manifest["command_exit_codes"] = [0]
    manifest_path.write_text(json.dumps(manifest))
    registry = target_registry()
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        target_registry_override=registry,
        target_executor_override=lambda *_args: None,
    )
    assert any("could not execute" in error for error in errors)


def test_r5_a04_claimed_zero_cannot_hide_real_exit_one(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path)
    manifest_path = tmp_path / evidence
    manifest = json.loads(manifest_path.read_text())
    manifest["command_exit_codes"] = [0]
    manifest_path.write_text(json.dumps(manifest))
    registry = target_registry()
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        target_registry_override=registry,
        target_executor_override=_failed_executor(registry),
    )
    assert any("actual_exit_code mismatch" in error for error in errors)


def test_r5_a05_fake_pass_log_cannot_hide_target_failure(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path)
    manifest_path = tmp_path / evidence
    manifest = json.loads(manifest_path.read_text())
    manifest["pass_log"] = "ALL TESTS PASSED"
    manifest_path.write_text(json.dumps(manifest))
    registry = target_registry()
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        target_registry_override=registry,
        target_executor_override=_failed_executor(registry),
    )
    assert any("test_results mismatch" in error for error in errors)


def test_r5_a06_reviewer_gate_is_informational_only(tmp_path: Path) -> None:
    evidence = valid_manifest(tmp_path)
    manifest_path = tmp_path / evidence
    manifest = json.loads(manifest_path.read_text())
    manifest["reviewer_gate"] = "PASS"
    manifest["verification_targets"] = []
    manifest_path.write_text(json.dumps(manifest))
    errors = validate(
        tmp_path,
        stage="REQUIREMENT_VERIFICATION",
        result="PASS",
        evidence=evidence,
        independent_evidence=evidence,
    )
    assert any("verification_targets must be a non-empty" in error for error in errors)


def _fixture_target(nodeid: str, acceptance_ids: list[str]) -> dict[str, object]:
    return {
        "requirement_id": "REQ-TEST-001",
        "acceptance_ids": acceptance_ids,
        "change_id": "CHANGE-001",
        "slice_id": "C001-S1",
        "verification_stage": "IMPLEMENTATION",
        "verification_level": "INTEGRATION",
        "runner": "pytest",
        "setup": "none",
        "working_directory": ".",
        "arguments": [nodeid],
        "test_nodes": [
            {
                "nodeid": nodeid,
                "requirement_id": "REQ-TEST-001",
                "acceptance_ids": acceptance_ids,
            }
        ],
        "receipt_path": "docs/quality/evidence/receipts/fixture.json",
    }


def test_r5_a07_comment_text_does_not_create_binding() -> None:
    nodeid = "apps/api/tests/fixtures/quality_binding_cases.py::test_comment_only"
    target = _fixture_target(nodeid, ["AC-TEST-001"])
    registry = {"schema_version": 1, "targets": {"VT-FIXTURE": target}}
    receipt = VerificationRuntime(root=ROOT, registry=registry).execute(
        target_id="VT-FIXTURE", target=target, source_fingerprint="fixture"
    )
    errors: list[str] = []
    validate_execution_receipt(
        target_id="VT-FIXTURE",
        target=target,
        receipt=receipt,
        source_fingerprint_value="fixture",
        target_registry=registry,
        errors=errors,
    )
    assert any("collected bindings mismatch" in error for error in errors)


def _acceptance(requirement: str, acceptance_id: str) -> dict[str, str]:
    return {
        "id": acceptance_id,
        "requirement": requirement,
        "given": "given",
        "when": "when",
        "then": "then",
        "verification": "test",
        "evidence": "receipt",
    }


def test_r5_a08_structured_marker_with_unknown_ac_fails() -> None:
    nodeid = (
        "apps/api/tests/fixtures/quality_binding_cases.py::test_unknown_requirement_and_acceptance"
    )
    registry = {
        "schema_version": 1,
        "targets": {"VT-FIXTURE": _fixture_target(nodeid, ["AC-MISSING-001"])},
    }
    errors = validate_verification_target_registry(
        registry=registry,
        catalog_by_id=catalog(),
        acceptance_by_id={"AC-TEST-001": _acceptance("REQ-TEST-001", "AC-TEST-001")},
        scope_registry=scope_registry(),
        root=ROOT,
    )
    assert any("AC does not belong" in error for error in errors)


def test_r5_a09_structured_marker_with_foreign_ac_fails() -> None:
    nodeid = "apps/api/tests/fixtures/quality_binding_cases.py::test_wrong_acceptance_owner"
    registry = {
        "schema_version": 1,
        "targets": {"VT-FIXTURE": _fixture_target(nodeid, ["AC-OTHER-001"])},
    }
    errors = validate_verification_target_registry(
        registry=registry,
        catalog_by_id=catalog(),
        acceptance_by_id={
            "AC-TEST-001": _acceptance("REQ-TEST-001", "AC-TEST-001"),
            "AC-OTHER-001": _acceptance("REQ-OTHER-001", "AC-OTHER-001"),
        },
        scope_registry=scope_registry(),
        root=ROOT,
    )
    assert any("AC does not belong" in error for error in errors)


def test_r5_a10_valid_collected_marker_and_actual_pass_is_valid() -> None:
    nodeid = "apps/api/tests/fixtures/quality_binding_cases.py::test_valid_binding"
    target = _fixture_target(nodeid, ["AC-TEST-001"])
    registry = {"schema_version": 1, "targets": {"VT-FIXTURE": target}}
    receipt = VerificationRuntime(root=ROOT, registry=registry).execute(
        target_id="VT-FIXTURE", target=target, source_fingerprint="fixture"
    )
    errors: list[str] = []
    validate_execution_receipt(
        target_id="VT-FIXTURE",
        target=target,
        receipt=receipt,
        source_fingerprint_value="fixture",
        target_registry=registry,
        errors=errors,
    )
    assert errors == []


def test_r5_a11_source_change_invalidates_old_receipt(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path)
    (tmp_path / "src/implementation.py").write_text("VALUE = 2\n")
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
    )
    assert any("source_fingerprint does not match" in error for error in errors)


def test_r5_a12_target_change_invalidates_old_receipt(tmp_path: Path) -> None:
    evidence = valid_attestation(tmp_path)
    registry = target_registry()
    registry["targets"]["VT-TEST-IMPLEMENTATION"]["setup"] = "guarded_postgres"
    errors = validate(
        tmp_path,
        stage="CODE_REVIEW_READY",
        result="IMPLEMENTED_UNVERIFIED",
        evidence=evidence,
        target_registry_override=registry,
    )
    assert any("target definition is stale" in error for error in errors)
