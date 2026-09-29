#!/usr/bin/env python3
"""Execute repository-owned verification targets and produce runner receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "docs/quality/verification-targets.json"
PLUGIN = "scripts.quality.pytest_binding_plugin"


class VerificationExecutionError(RuntimeError):
    """Raised when fixed verification-target setup cannot be completed."""


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def repository_head(root: Path) -> str:
    completed = _run(["git", "rev-parse", "HEAD"], root=root, env=os.environ.copy())
    head = completed.stdout.strip()
    if completed.returncode != 0 or len(head) != 40:
        raise VerificationExecutionError("unable to resolve verification base HEAD")
    return head


def load_target_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("verification target registry must be a JSON object")
    return value


def implementation_fingerprint_for_target(*, root: Path, target: dict[str, object]) -> str:
    requirement_id = target.get("requirement_id")
    change_id = target.get("change_id")
    slice_id = target.get("slice_id")
    matches: list[str] = []
    evidence_root = root / "docs/quality/evidence"
    for path in evidence_root.glob("**/implementation/*.json"):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(manifest, dict):
            continue
        if (
            manifest.get("requirement_id") == requirement_id
            and manifest.get("change_id") == change_id
            and manifest.get("slice_id") == slice_id
            and manifest.get("coverage") == "FULL"
            and isinstance(manifest.get("source_fingerprint"), str)
        ):
            matches.append(str(manifest["source_fingerprint"]))
    if len(matches) != 1:
        raise VerificationExecutionError(
            "canonical target requires exactly one matching Implementation Attestation: "
            f"{requirement_id}"
        )
    return matches[0]


def _run(argv: list[str], *, root: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


class VerificationRuntime:
    """Runs allowlisted target definitions once per source fingerprint."""

    def __init__(self, *, root: Path, registry: dict[str, object]) -> None:
        self.root = root
        self.registry = registry
        self.registry_hash = canonical_hash(registry)
        self._guarded_postgres_ready = False
        self._cache: dict[tuple[str, str], dict[str, object]] = {}

    def _environment(self) -> dict[str, str]:
        env = os.environ.copy()
        env.pop("PYTEST_ADDOPTS", None)
        env.pop("PYTEST_PLUGINS", None)
        env.setdefault(
            "TEST_DATABASE_URL",
            "postgresql+psycopg://needradar_test:needradar_test_local@127.0.0.1:55432/needradar_test",
        )
        env.setdefault(
            "TEST_DATABASE_ADMIN_URL",
            "postgresql+psycopg://needradar_test:needradar_test_local@127.0.0.1:55432/postgres",
        )
        env.setdefault(
            "DATABASE_URL",
            "postgresql+psycopg://needradar:needradar_local@127.0.0.1:5432/needradar",
        )
        env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
        return env

    def _prepare_guarded_postgres(self, env: dict[str, str]) -> None:
        if self._guarded_postgres_ready:
            return
        commands = [
            ["docker", "compose", "up", "-d", "--wait", "postgres-test"],
            [
                "uv",
                "run",
                "python",
                "-m",
                "needradar.testing.database_safety",
                "bootstrap",
            ],
            [
                "uv",
                "run",
                "python",
                "-m",
                "needradar.testing.database_safety",
                "prepare",
            ],
        ]
        env = {**env, "PYTHONPATH": "apps/api/src"}
        for argv in commands:
            completed = _run(argv, root=self.root, env=env)
            if completed.returncode != 0:
                raise VerificationExecutionError(
                    "guarded PostgreSQL setup failed for canonical verification target: "
                    + " ".join(argv)
                    + "\n"
                    + completed.stderr[-2000:]
                )
        self._guarded_postgres_ready = True

    def execute(
        self,
        *,
        target_id: str,
        target: dict[str, object],
        source_fingerprint: str,
    ) -> dict[str, object]:
        cache_key = (target_id, source_fingerprint)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        if target.get("runner") != "pytest":
            raise VerificationExecutionError(f"unsupported verification runner: {target_id}")
        arguments = target.get("arguments")
        if not isinstance(arguments, list) or not all(isinstance(arg, str) for arg in arguments):
            raise VerificationExecutionError(f"invalid verification target arguments: {target_id}")
        nodes = target.get("test_nodes")
        declared_nodeids = (
            [node.get("nodeid") for node in nodes if isinstance(node, dict)]
            if isinstance(nodes, list)
            else []
        )
        if arguments != declared_nodeids or any(
            argument.startswith("-")
            or "::" not in argument
            or Path(argument.split("::", 1)[0]).is_absolute()
            or ".." in Path(argument.split("::", 1)[0]).parts
            for argument in arguments
        ):
            raise VerificationExecutionError(
                f"verification target must contain only exact declared pytest node IDs: {target_id}"
            )
        if target.get("working_directory") != "." or target.get("setup") not in {
            "none",
            "guarded_postgres",
        }:
            raise VerificationExecutionError(f"invalid fixed execution policy: {target_id}")

        env = self._environment()
        if target.get("setup") == "guarded_postgres":
            self._prepare_guarded_postgres(env)

        with tempfile.TemporaryDirectory(prefix="needradar-verification-") as directory:
            temporary = Path(directory)
            bindings_path = temporary / "bindings.json"
            results_path = temporary / "results.json"
            collect_env = {**env, "NEEDRADAR_BINDINGS_OUTPUT": str(bindings_path)}
            collection_argv = [
                "uv",
                "run",
                "pytest",
                "--collect-only",
                "-q",
                "-p",
                PLUGIN,
                *arguments,
            ]
            collected = _run(collection_argv, root=self.root, env=collect_env)
            collection_data: dict[str, Any] = {"nodes": [], "bindings": []}
            if collected.returncode == 0 and bindings_path.is_file():
                loaded = json.loads(bindings_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    collection_data = loaded

            execution_env = {**env, "NEEDRADAR_RESULTS_OUTPUT": str(results_path)}
            execution_argv = [
                "uv",
                "run",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "-p",
                PLUGIN,
                *arguments,
            ]
            started_at = utc_now()
            if collected.returncode == 0:
                executed = _run(execution_argv, root=self.root, env=execution_env)
            else:
                executed = subprocess.CompletedProcess(
                    execution_argv, collected.returncode, "", "collection failed"
                )
            finished_at = utc_now()
            result_data: dict[str, Any] = {"results": {}}
            if results_path.is_file():
                loaded = json.loads(results_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    result_data = loaded

        receipt: dict[str, object] = {
            "schema_version": 2,
            "receipt_id": hashlib.sha256(
                f"{target_id}\0{source_fingerprint}\0{started_at}".encode()
            ).hexdigest(),
            "target_id": target_id,
            "requirement_id": target.get("requirement_id"),
            "acceptance_ids": target.get("acceptance_ids"),
            "verification_stage": target.get("verification_stage"),
            "verification_level": target.get("verification_level"),
            "verification_base_head": repository_head(self.root),
            "target_registry_hash": self.registry_hash,
            "target_definition_hash": canonical_hash(target),
            "source_fingerprint": source_fingerprint,
            "collection_argv": collection_argv,
            "collection_exit_code": collected.returncode,
            "collected_nodes": collection_data.get("nodes", []),
            "collected_bindings": collection_data.get("bindings", []),
            "exact_executable_argv": execution_argv,
            "started_at": started_at,
            "finished_at": finished_at,
            "executed_at": finished_at,
            "actual_exit_code": executed.returncode,
            "test_results": result_data.get("results", {}),
            "stdout_sha256": hashlib.sha256(executed.stdout.encode()).hexdigest(),
            "stderr_sha256": hashlib.sha256(executed.stderr.encode()).hexdigest(),
            "working_directory": ".",
        }
        self._cache[cache_key] = receipt
        return receipt


def write_receipt(root: Path, reference: str, receipt: dict[str, object]) -> str:
    path = root / reference
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return file_sha256(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--attestation", action="append")
    source.add_argument("--target", action="append")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--no-write-receipt", action="store_true")
    args = parser.parse_args()
    registry_path = Path(args.registry)
    registry = load_target_registry(registry_path)
    targets = registry.get("targets")
    if not isinstance(targets, dict):
        raise SystemExit("verification target registry lacks targets")
    runtime = VerificationRuntime(root=ROOT, registry=registry)
    requests: list[tuple[str, str]] = []
    for reference in args.attestation or []:
        manifest = json.loads((ROOT / reference).read_text(encoding="utf-8"))
        requests.extend(
            (target_id, str(manifest["source_fingerprint"]))
            for target_id in manifest["verification_targets"]
        )
    for target_id in args.target or []:
        target = targets.get(target_id)
        if not isinstance(target, dict):
            raise SystemExit(f"unknown canonical verification target: {target_id}")
        requests.append(
            (
                target_id,
                implementation_fingerprint_for_target(root=ROOT, target=target),
            )
        )

    failed = False
    for target_id, fingerprint in requests:
        target = targets.get(target_id)
        if not isinstance(target, dict):
            raise SystemExit(f"unknown canonical verification target: {target_id}")
        receipt = runtime.execute(
            target_id=target_id,
            target=target,
            source_fingerprint=fingerprint,
        )
        if args.no_write_receipt:
            digest = canonical_hash(receipt)
            receipt_ref = "NOT_WRITTEN"
        else:
            receipt_ref = target["receipt_path"]
            if not isinstance(receipt_ref, str):
                raise SystemExit(f"canonical target lacks receipt path: {target_id}")
            digest = write_receipt(ROOT, receipt_ref, receipt)
        print(
            f"{target_id} {receipt_ref} {digest} "
            f"exit={receipt['actual_exit_code']} base={receipt['verification_base_head']}"
        )
        if receipt["collection_exit_code"] != 0 or receipt["actual_exit_code"] != 0:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
