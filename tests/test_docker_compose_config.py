"""Static tests for local Docker startup configuration."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runs_the_unified_python_entrypoint():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.12" in dockerfile
    assert 'pip install --no-cache-dir -e ".[dev]"' in dockerfile
    assert "EXPOSE 8000" in dockerfile
    assert 'CMD ["python", "-m", "app"]' in dockerfile


def test_compose_defines_local_app_postgres_and_redis_services():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))

    services = compose["services"]
    assert set(services) == {"postgres", "redis", "app"}
    assert services["app"]["build"]["context"] == "."
    assert services["app"]["command"] == ["python", "-m", "app"]
    assert services["app"]["ports"] == ["8000:8000"]
    assert services["app"]["depends_on"] == {
        "postgres": {"condition": "service_healthy"},
        "redis": {"condition": "service_healthy"},
    }
    assert services["app"]["environment"]["DATABASE_URL"] == (
        "postgresql+psycopg://postgres:postgres@postgres:5432/translation"
    )
    assert services["app"]["environment"]["REDIS_URL"] == "redis://redis:6379/0"
    assert services["app"]["environment"]["RQ_QUEUE_NAME"] == "translation"


def test_compose_persists_postgres_data_and_has_healthchecks():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))

    assert "postgres_data" in compose["volumes"]
    assert compose["services"]["postgres"]["healthcheck"]["test"] == [
        "CMD-SHELL",
        "pg_isready -U postgres -d translation",
    ]
    assert compose["services"]["redis"]["healthcheck"]["test"] == [
        "CMD",
        "redis-cli",
        "ping",
    ]
