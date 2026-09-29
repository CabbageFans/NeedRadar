from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol


class WorkerRole(StrEnum):
    CRAWLER = "crawler_worker"
    ANALYSIS = "analysis_worker"
    CLUSTERING = "clustering_worker"


class TaskHandler(Protocol):
    async def __call__(self, payload: dict[str, Any]) -> None: ...


@dataclass(frozen=True, slots=True)
class WorkerBoundary:
    role: WorkerRole
    task_namespace: str
    handler: TaskHandler | None = None

    @property
    def available(self) -> bool:
        return self.handler is not None


class WorkerUnavailableError(RuntimeError):
    pass


class WorkerRegistry:
    def __init__(self, boundaries: tuple[WorkerBoundary, ...]) -> None:
        self._boundaries = {boundary.role: boundary for boundary in boundaries}

    def inventory(self) -> tuple[WorkerBoundary, ...]:
        return tuple(self._boundaries[role] for role in WorkerRole)

    async def dispatch(self, role: WorkerRole, payload: dict[str, Any]) -> None:
        boundary = self._boundaries[role]
        if boundary.handler is None:
            raise WorkerUnavailableError(f"{role.value} has no S1 business handler")
        await boundary.handler(payload)


DEFAULT_WORKER_REGISTRY = WorkerRegistry(
    tuple(
        WorkerBoundary(role=role, task_namespace=f"needradar.{role.value}") for role in WorkerRole
    )
)
