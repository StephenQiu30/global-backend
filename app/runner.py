"""Unified process entry: schema init, RQ worker, and API server."""

from __future__ import annotations

import multiprocessing as mp
import os
from multiprocessing.process import BaseProcess

import uvicorn

from app.core.config import Settings
from app.db.schema import init_schema


def _run_rq_worker() -> None:
    """RQ worker process entrypoint."""
    from redis import Redis
    from rq import Queue, Worker

    settings = Settings()
    connection = Redis.from_url(settings.redis_url)
    queues = [Queue(settings.rq_queue_name, connection=connection)]
    worker = Worker(queues, connection=connection)
    worker.work()


def _start_worker(settings: Settings) -> BaseProcess:
    """Start one background RQ worker for the configured queue."""
    ctx = mp.get_context("spawn")
    worker = ctx.Process(target=_run_rq_worker, name="rq-worker", daemon=True)
    worker.start()
    print(f"Started RQ worker (pid={worker.pid}, queue={settings.rq_queue_name})")
    return worker


def _run_api(host: str, port: int) -> None:
    """Run the FastAPI application through Uvicorn."""
    print(f"Starting API at http://{host}:{port} (docs: /docs)")
    uvicorn.run("app.main:app", host=host, port=port, log_level="info")


def _shutdown_worker(worker: BaseProcess) -> None:
    """Terminate the worker child process when API shutdown begins."""
    if worker.is_alive():
        worker.terminate()
        worker.join(timeout=5)


def main() -> None:
    """Initialize infrastructure and start API plus background worker."""
    settings = Settings()
    target = settings.database_url.rsplit("@", 1)[-1]
    print(f"Initializing database schema on {target}...")
    init_schema(settings.database_url)

    worker = _start_worker(settings)
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))

    try:
        _run_api(host, port)
    finally:
        _shutdown_worker(worker)


if __name__ == "__main__":
    main()
