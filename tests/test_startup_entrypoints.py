"""Static tests for the accepted project startup entrypoints."""

from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_does_not_define_console_startup_script():
    """The project must not expose an extra console command startup path."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "scripts" not in pyproject.get("project", {})


def test_legacy_init_db_script_is_removed():
    """Schema initialization belongs to python -m app, not a separate script."""
    assert not (ROOT / "scripts/init_db.py").exists()


def test_python_module_main_remains_the_local_entrypoint():
    """python -m app must continue to delegate to app.runner.main."""
    module_main = (ROOT / "app/__main__.py").read_text(encoding="utf-8")

    assert "from app.runner import main" in module_main
    assert "main()" in module_main
