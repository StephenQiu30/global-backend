"""Tests for the unified local startup runner."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FakeSettings:
    database_url: str = "postgresql+psycopg://user:pass@localhost:5432/translation"
    redis_url: str = "redis://localhost:6379/0"
    rq_queue_name: str = "translation"


class FakeWorker:
    pid = 1234

    def __init__(self) -> None:
        self.terminated = False
        self.join_timeout: int | None = None

    def is_alive(self) -> bool:
        return True

    def terminate(self) -> None:
        self.terminated = True

    def join(self, timeout: int | None = None) -> None:
        self.join_timeout = timeout


def test_main_initializes_schema_starts_worker_runs_api_and_stops_worker(monkeypatch):
    """main must initialize DB, start one worker, run API, then stop the worker."""
    events: list[tuple[str, object]] = []
    worker = FakeWorker()

    monkeypatch.setattr("app.runner.Settings", lambda: FakeSettings())
    monkeypatch.setattr("app.runner.init_schema", lambda url: events.append(("schema", url)))
    monkeypatch.setattr(
        "app.runner._start_worker",
        lambda settings: events.append(("worker", settings.rq_queue_name)) or worker,
    )
    monkeypatch.setattr(
        "app.runner._run_api",
        lambda host, port: events.append(("api", f"{host}:{port}")),
    )
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8765")

    from app.runner import main

    main()

    assert events == [
        ("schema", "postgresql+psycopg://user:pass@localhost:5432/translation"),
        ("worker", "translation"),
        ("api", "127.0.0.1:8765"),
    ]
    assert worker.terminated is True
    assert worker.join_timeout == 5


def test_shutdown_worker_skips_terminate_when_worker_already_stopped():
    """Stopped workers must not receive terminate during shutdown."""

    class StoppedWorker(FakeWorker):
        def is_alive(self) -> bool:
            return False

    worker = StoppedWorker()

    from app.runner import _shutdown_worker

    _shutdown_worker(worker)

    assert worker.terminated is False
    assert worker.join_timeout is None
