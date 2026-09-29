from __future__ import annotations

import uvicorn

from needradar.core.config import load_settings
from needradar.core.logging import uvicorn_log_config


def main() -> None:
    settings = load_settings()
    uvicorn.run(
        "needradar.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        log_config=uvicorn_log_config(settings.log_level),
    )


if __name__ == "__main__":
    main()
