from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]


def dependency_major(package: dict[str, object], section: str, dependency: str) -> int:
    dependencies = package.get(section)
    assert isinstance(dependencies, dict), f"package.json lacks {section}"
    version = dependencies.get(dependency)
    assert isinstance(version, str), f"package.json lacks {section}.{dependency}"
    match = re.match(r"^[^0-9]*(\d+)(?:\.|$)", version)
    assert match is not None, f"{dependency} has no enforceable major version: {version}"
    return int(match.group(1))


def assert_frontend_baseline(web_root: Path) -> None:
    package = json.loads((web_root / "package.json").read_text(encoding="utf-8"))
    assert dependency_major(package, "dependencies", "next") >= 15, (
        "REQ-ARCH-010 requires Next.js 15+"
    )
    assert dependency_major(package, "dependencies", "react") >= 19, (
        "REQ-ARCH-010 requires React 19+"
    )
    assert dependency_major(package, "dependencies", "react-dom") >= 19, (
        "REQ-ARCH-010 requires React DOM 19+"
    )
    dependency_major(package, "devDependencies", "typescript")
    dependency_major(package, "devDependencies", "tailwindcss")

    scripts = package.get("scripts")
    assert isinstance(scripts, dict)
    assert all(
        isinstance(scripts.get(name), str) and str(scripts[name]).startswith(command)
        for name, command in {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
        }.items()
    ), "Next.js must be the configured frontend runtime and build system"

    tsconfig = json.loads((web_root / "tsconfig.json").read_text(encoding="utf-8"))
    compiler_options = tsconfig.get("compilerOptions")
    assert isinstance(compiler_options, dict)
    assert compiler_options.get("strict") is True
    assert compiler_options.get("allowJs") is False
    assert compiler_options.get("jsx") == "preserve"
    plugins = compiler_options.get("plugins")
    assert isinstance(plugins, list) and {"name": "next"} in plugins

    tailwind_config = (web_root / "tailwind.config.ts").read_text(encoding="utf-8")
    assert "./app/**/*.{js,ts,jsx,tsx,mdx}" in tailwind_config
    assert "./src/**/*.{js,ts,jsx,tsx,mdx}" in tailwind_config
    postcss_config = (web_root / "postcss.config.mjs").read_text(encoding="utf-8")
    assert "tailwindcss" in postcss_config
    globals_css = (web_root / "app/globals.css").read_text(encoding="utf-8")
    for directive in ("@tailwind base;", "@tailwind components;", "@tailwind utilities;"):
        assert directive in globals_css
    layout = (web_root / "app/layout.tsx").read_text(encoding="utf-8")
    assert 'import "./globals.css";' in layout
    dashboard = (web_root / "app/dashboard/page.tsx").read_text(encoding="utf-8")
    assert "className=" in dashboard and "min-h-screen" in dashboard


@pytest.fixture
def frontend_baseline_fixture(tmp_path: Path) -> Path:
    web_root = tmp_path / "web"
    (web_root / "app/dashboard").mkdir(parents=True)
    for relative in (
        "package.json",
        "tsconfig.json",
        "tailwind.config.ts",
        "postcss.config.mjs",
        "app/globals.css",
        "app/layout.tsx",
        "app/dashboard/page.tsx",
    ):
        source = ROOT / "apps/web" / relative
        destination = web_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    return web_root


def run_repository_command(argv: list[str], *, env: dict[str, str] | None = None) -> None:
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, (
        f"canonical verification command failed: {argv}\n"
        f"stdout:\n{completed.stdout[-4000:]}\n"
        f"stderr:\n{completed.stderr[-4000:]}"
    )


@pytest.mark.quality_binding("REQ-ARCH-010")
def test_arch_010_frontend_baseline() -> None:
    assert_frontend_baseline(ROOT / "apps/web")


@pytest.mark.quality_binding("REQ-ARCH-010")
def test_arch_010_rejects_incompatible_frontend_fixture(
    frontend_baseline_fixture: Path,
) -> None:
    package_path = frontend_baseline_fixture / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["dependencies"]["next"] = "14.2.0"
    package_path.write_text(json.dumps(package), encoding="utf-8")

    with pytest.raises(AssertionError, match=r"Next\.js 15\+"):
        assert_frontend_baseline(frontend_baseline_fixture)


@pytest.mark.quality_binding("REQ-ARCH-002")
def test_arch_002_backend_baseline_declarations() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    engine = (ROOT / "apps/api/src/needradar/db/engine.py").read_text(encoding="utf-8")

    for dependency in ("fastapi", "sqlalchemy[asyncio]", "alembic", "psycopg[binary]"):
        assert f'"{dependency}' in pyproject
    assert re.search(r"image:\s+postgres:18(?:\.|-)", compose)
    assert "create_async_engine" in engine


@pytest.mark.quality_binding("REQ-FOUNDATION-001", "AC-FOUNDATION-001")
def test_foundation_scope_remains_s1_only() -> None:
    run_repository_command(["uv", "run", "python", "scripts/quality/check_s1_scope.py"])


@pytest.mark.quality_binding("REQ-FOUNDATION-001", "AC-FOUNDATION-001")
def test_foundation_real_e2e() -> None:
    env = os.environ.copy()
    env.setdefault("API_PORT", "18123")
    env.setdefault("WEB_PORT", "31123")
    run_repository_command(
        ["pnpm", "exec", "playwright", "test", "tests/e2e/foundation.spec.ts"],
        env=env,
    )
