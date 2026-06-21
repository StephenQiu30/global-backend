"""Tests for documented local startup commands."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_only_supported_startup_paths():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "python -m app" in readme
    assert "docker compose up --build" in readme
    assert "docker compose down" in readme
    assert "docker compose down -v" in readme
    assert "http://127.0.0.1:8000/docs" in readme
    assert "```bash\nglobal-backend\n```" not in readme
    assert "scripts/init_db.py" not in readme
    assert "uvicorn app.main:app" not in readme


def test_operations_doc_documents_only_supported_startup_paths():
    doc = (ROOT / "docs/operations/local-development.md").read_text(encoding="utf-8")

    assert "python -m app" in doc
    assert "docker compose up --build" in doc
    assert "docker compose down" in doc
    assert "docker compose down -v" in doc
    assert "http://127.0.0.1:8000/docs" in doc
    assert "```bash\nglobal-backend\n```" not in doc
    assert "scripts/init_db.py" not in doc
    assert "uvicorn app.main:app" not in doc
