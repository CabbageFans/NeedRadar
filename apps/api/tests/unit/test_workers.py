from __future__ import annotations

import pytest
from needradar.workers import DEFAULT_WORKER_REGISTRY, WorkerRole
from needradar.workers.registry import WorkerUnavailableError

pytestmark = pytest.mark.unit


@pytest.mark.quality_binding("REQ-ARCH-013")
def test_worker_roles_are_distinct_and_unavailable_in_s1() -> None:
    inventory = DEFAULT_WORKER_REGISTRY.inventory()
    assert [item.role for item in inventory] == list(WorkerRole)
    assert {item.task_namespace for item in inventory} == {
        "needradar.crawler_worker",
        "needradar.analysis_worker",
        "needradar.clustering_worker",
    }
    assert all(not item.available for item in inventory)


@pytest.mark.asyncio
@pytest.mark.quality_binding("REQ-ARCH-013")
async def test_worker_boundary_does_not_fake_business_execution() -> None:
    with pytest.raises(WorkerUnavailableError, match="no S1 business handler"):
        await DEFAULT_WORKER_REGISTRY.dispatch(WorkerRole.CRAWLER, {})
