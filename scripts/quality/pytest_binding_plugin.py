"""Emit structured NeedRadar quality bindings and executed-node outcomes for pytest."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_RESULTS: dict[str, str] = {}


def _binding_from_marker(nodeid: str, marker: Any) -> dict[str, object]:
    if not marker.args or not isinstance(marker.args[0], str):
        return {
            "nodeid": nodeid,
            "requirement_id": None,
            "acceptance_ids": [],
            "invalid": "quality_binding requires a Requirement ID string",
        }
    acceptance_ids = list(marker.args[1:])
    if not all(isinstance(value, str) and value for value in acceptance_ids):
        return {
            "nodeid": nodeid,
            "requirement_id": marker.args[0],
            "acceptance_ids": [],
            "invalid": "quality_binding Acceptance IDs must be non-empty strings",
        }
    return {
        "nodeid": nodeid,
        "requirement_id": marker.args[0],
        "acceptance_ids": acceptance_ids,
    }


def pytest_collection_finish(session: Any) -> None:
    output = os.environ.get("NEEDRADAR_BINDINGS_OUTPUT")
    if not output:
        return
    bindings: list[dict[str, object]] = []
    nodes: list[str] = []
    for item in session.items:
        nodes.append(item.nodeid)
        for marker in item.iter_markers(name="quality_binding"):
            bindings.append(_binding_from_marker(item.nodeid, marker))
    Path(output).write_text(
        json.dumps({"nodes": nodes, "bindings": bindings}, indent=2) + "\n",
        encoding="utf-8",
    )


def pytest_configure(config: Any) -> None:
    _RESULTS.clear()


def pytest_runtest_logreport(report: Any) -> None:
    if report.when != "call":
        return
    _RESULTS[report.nodeid] = report.outcome


def pytest_sessionfinish(session: Any) -> None:
    output = os.environ.get("NEEDRADAR_RESULTS_OUTPUT")
    if not output:
        return
    Path(output).write_text(
        json.dumps({"results": _RESULTS}, indent=2) + "\n",
        encoding="utf-8",
    )
