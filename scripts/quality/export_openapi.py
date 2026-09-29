from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "apps/api/src"))

from needradar.api.app import create_app  # noqa: E402
from needradar.core.config import Settings  # noqa: E402


def render_schema() -> str:
    app = create_app(Settings(_env_file=None))
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: export_openapi.py OUTPUT")
    Path(sys.argv[1]).write_text(render_schema())
