# Unified Local Startup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one local Python main startup entrypoint plus one Docker Compose startup path for `global-backend`, and remove extra project startup entrypoints.

**Architecture:** `app.runner:main` remains the only process-level entrypoint for local development. It loads settings, initializes ORM schema, starts one RQ worker child process, starts Uvicorn, and shuts the worker down when the API exits. Docker Compose provides PostgreSQL, Redis, and the app container running the same `python -m app` command.

**Tech Stack:** Python 3.12+, FastAPI, Uvicorn, SQLAlchemy 2.x, PostgreSQL, Redis, RQ, Docker Compose, pytest.

## Global Constraints

- Local Python startup command is `python -m app`.
- Docker startup command is `docker compose up --build`.
- Docker services are `postgres`, `redis`, and `app`.
- Compose app `DATABASE_URL` is `postgresql+psycopg://postgres:postgres@postgres:5432/translation`.
- Compose app `REDIS_URL` is `redis://redis:6379/0`.
- Compose app `RQ_QUEUE_NAME` is `translation`.
- `app/__main__.py` stays thin and only calls `app.runner:main`.
- `app/main.py` stays the FastAPI app factory and must not own process orchestration.
- No production deployment design.
- No separate Docker profiles for API and worker in the first version.
- No Kubernetes, Helm, Procfile, or process manager.
- No replacement of SQLAlchemy schema initialization with Alembic migrations in this startup design.
- No frontend container.
- Do not keep `global-backend` as an installed console startup command.
- Do not keep `scripts/init_db.py` as a standalone database startup helper.
- Do not document raw `uvicorn app.main:app` as a project startup command.

---

## File Structure

- Modify `app/runner.py`: keep `main()` as the process orchestrator and split small helper functions so startup behavior can be unit tested without opening sockets or Redis connections.
- Keep `app/__main__.py`: preserve the thin module entrypoint for `python -m app`.
- Modify `pyproject.toml`: remove the `[project.scripts]` startup entry so `python -m app` is the only local Python entrypoint.
- Delete `scripts/init_db.py`: remove the old database-only helper because `app.runner:main` owns schema initialization.
- Create `tests/test_startup_entrypoints.py`: static tests that reject extra startup entrypoints.
- Create `tests/test_runner.py`: unit tests for `main()`, worker startup, Uvicorn delegation, and worker shutdown.
- Create `Dockerfile`: local development image for the backend app.
- Create `docker-compose.yml`: local PostgreSQL, Redis, and app service orchestration.
- Create `tests/test_docker_compose_config.py`: static checks for the Docker and Compose contract without requiring Docker daemon availability.
- Modify `README.md`: document local Python, installed command, Docker Compose, API docs URL, stop/reset commands.
- Modify `docs/operations/local-development.md`: add the same startup choices for developer onboarding.

---

### Task 1: Remove Extra Startup Entrypoints

**Files:**
- Modify: `pyproject.toml`
- Delete: `scripts/init_db.py`
- Test: `tests/test_startup_entrypoints.py`

**Interfaces:**
- Consumes: `pyproject.toml`, `scripts/init_db.py`, `app/__main__.py`.
- Produces: a single local Python project entrypoint, `python -m app`.

- [ ] **Step 1: Write failing tests for entrypoint cleanup**

Create `tests/test_startup_entrypoints.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_startup_entrypoints.py -v
```

Expected: FAIL because `pyproject.toml` still defines `[project.scripts]` and `scripts/init_db.py` still exists.

- [ ] **Step 3: Remove console script from `pyproject.toml`**

Delete this block from `pyproject.toml`:

```toml
[project.scripts]
global-backend = "app.runner:main"
```

- [ ] **Step 4: Delete the legacy init script**

Delete `scripts/init_db.py`.

- [ ] **Step 5: Run entrypoint cleanup tests**

Run:

```bash
pytest tests/test_startup_entrypoints.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 1**

```bash
git add pyproject.toml tests/test_startup_entrypoints.py
git rm scripts/init_db.py
git commit -m "chore: keep only main startup entrypoint"
```

---

### Task 2: Testable Python Main Entrypoint

**Files:**
- Modify: `app/runner.py`
- Keep: `app/__main__.py`
- Test: `tests/test_runner.py`

**Interfaces:**
- Consumes: `app.core.config.Settings`, `app.db.schema.init_schema(database_url: str | None = None) -> None`, `app.main:app`.
- Produces: `app.runner.main() -> None`, `app.runner._run_rq_worker() -> None`, `app.runner._start_worker(settings: Settings) -> multiprocessing.Process`, `app.runner._run_api(host: str, port: int) -> None`, `app.runner._shutdown_worker(worker: multiprocessing.Process) -> None`.

- [ ] **Step 1: Write failing tests for orchestration and shutdown**

Create `tests/test_runner.py`:

```python
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
    monkeypatch.setattr("app.runner._start_worker", lambda settings: events.append(("worker", settings.rq_queue_name)) or worker)
    monkeypatch.setattr("app.runner._run_api", lambda host, port: events.append(("api", f"{host}:{port}")))
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_runner.py -v
```

Expected: FAIL because `app.runner.Settings`, `app.runner.init_schema`, `_start_worker`, `_run_api`, or `_shutdown_worker` cannot be patched consistently until imports and helper functions are module-level.

- [ ] **Step 3: Refactor `app/runner.py` to expose testable helpers**

Replace `app/runner.py` with:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
pytest tests/test_runner.py -v
```

Expected: PASS.

- [ ] **Step 5: Verify existing startup-adjacent tests still pass**

Run:

```bash
pytest tests/test_config.py tests/db/test_init_db.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add app/runner.py tests/test_runner.py
git commit -m "test: cover unified startup runner"
```

---

### Task 3: Docker Image And Compose Stack

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Test: `tests/test_docker_compose_config.py`

**Interfaces:**
- Consumes: `python -m app`, `pyproject.toml`, `.env.example`.
- Produces: Local Docker command `docker compose up --build` with services `postgres`, `redis`, and `app`.

- [ ] **Step 1: Write failing static config tests**

Create `tests/test_docker_compose_config.py`:

```python
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
    assert compose["services"]["redis"]["healthcheck"]["test"] == ["CMD", "redis-cli", "ping"]
```

- [ ] **Step 2: Add PyYAML to dev dependencies if static tests cannot import `yaml`**

Modify `pyproject.toml` dev dependencies:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "respx>=0.22.0",
    "pytest-asyncio>=0.24.0",
    "pyyaml>=6.0.0",
]
```

- [ ] **Step 3: Run tests to verify they fail for missing Docker files**

Run:

```bash
pytest tests/test_docker_compose_config.py -v
```

Expected: FAIL with `FileNotFoundError` for `Dockerfile` or `docker-compose.yml`.

- [ ] **Step 4: Create `Dockerfile`**

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
COPY docs ./docs

RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

CMD ["python", "-m", "app"]
```

- [ ] **Step 5: Create `docker-compose.yml`**

Create `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: translation
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d translation"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 10

  app:
    build:
      context: .
    command: ["python", "-m", "app"]
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:postgres@postgres:5432/translation
      REDIS_URL: redis://redis:6379/0
      RQ_QUEUE_NAME: translation
      HOST: 0.0.0.0
      PORT: "8000"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  postgres_data:
```

- [ ] **Step 6: Run static Docker config tests**

Run:

```bash
pytest tests/test_docker_compose_config.py -v
```

Expected: PASS.

- [ ] **Step 7: Validate Compose syntax**

Run:

```bash
docker compose config
```

Expected: command exits 0 and prints normalized services `app`, `postgres`, and `redis`.

- [ ] **Step 8: Commit Task 3**

```bash
git add Dockerfile docker-compose.yml pyproject.toml tests/test_docker_compose_config.py
git commit -m "feat: add docker compose local startup"
```

---

### Task 4: Startup Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/operations/local-development.md`

**Interfaces:**
- Consumes: Task 2 `python -m app` and Task 3 `docker compose up --build`.
- Produces: Developer-facing startup docs with local Python main startup, Docker Compose, stop, reset, and docs URL.

- [ ] **Step 1: Write documentation contract tests**

Create `tests/test_startup_docs.py`:

```python
"""Tests for documented local startup commands."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_all_startup_paths():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "python -m app" in readme
    assert "docker compose up --build" in readme
    assert "docker compose down" in readme
    assert "docker compose down -v" in readme
    assert "http://127.0.0.1:8000/docs" in readme
    assert "```bash\nglobal-backend\n```" not in readme
    assert "scripts/init_db.py" not in readme
    assert "uvicorn app.main:app" not in readme


def test_operations_doc_documents_all_startup_paths():
    doc = (ROOT / "docs/operations/local-development.md").read_text(encoding="utf-8")

    assert "python -m app" in doc
    assert "docker compose up --build" in doc
    assert "docker compose down" in doc
    assert "docker compose down -v" in doc
    assert "http://127.0.0.1:8000/docs" in doc
    assert "```bash\nglobal-backend\n```" not in doc
    assert "scripts/init_db.py" not in doc
    assert "uvicorn app.main:app" not in doc
```

- [ ] **Step 2: Run tests to verify they fail until docs are updated**

Run:

```bash
pytest tests/test_startup_docs.py -v
```

Expected: FAIL because Docker Compose stop/reset commands are not fully documented in both files, and `global-backend` may still be documented.

- [ ] **Step 3: Update `README.md` quick start**

In `README.md`, replace the startup section under quick start with this Markdown:

    ### 3. 启动服务

    推荐本地开发方式：

    ```bash
    python -m app
    ```

    这条命令会按顺序完成数据库表初始化、启动一个 RQ Worker 子进程、启动 FastAPI API。

    Docker 一键启动 PostgreSQL、Redis 与后端：

    ```bash
    docker compose up --build
    ```

    停止 Docker 本地栈：

    ```bash
    docker compose down
    ```

    重置 Docker PostgreSQL 数据：

    ```bash
    docker compose down -v
    ```

    可选环境变量：`HOST`（默认 `0.0.0.0`）、`PORT`（默认 `8000`）。

    启动后访问 `http://127.0.0.1:8000/docs` 查看 API 文档。

- [ ] **Step 4: Update `docs/operations/local-development.md` local startup**

In `docs/operations/local-development.md`, replace the local startup section with this Markdown:

    ## 本地启动

    ### 推荐：本机 main 一键启动

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    cp .env.example .env
    # 编辑 .env，填写 GITHUB_APP_ID、GITHUB_PRIVATE_KEY、DATABASE_URL、REDIS_URL 等
    createdb translation
    python -m app
    ```

    ### Docker Compose 一体化启动

    ```bash
    cp .env.example .env
    # 编辑 .env，填写 GitHub / OpenAI 相关变量；Compose 会覆盖 DATABASE_URL 与 REDIS_URL
    docker compose up --build
    ```

    停止 Docker 本地栈：

    ```bash
    docker compose down
    ```

    重置 Docker PostgreSQL 数据：

    ```bash
    docker compose down -v
    ```

    服务启动后：

    - API 根路径：`http://127.0.0.1:8000`
    - OpenAPI 文档：`http://127.0.0.1:8000/docs`

- [ ] **Step 5: Run documentation tests**

Run:

```bash
pytest tests/test_startup_docs.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 4**

```bash
git add README.md docs/operations/local-development.md tests/test_startup_docs.py
git commit -m "docs: document unified local startup"
```

---

### Task 5: End-To-End Validation

**Files:**
- Modify only if validation reveals a startup defect: `app/runner.py`, `Dockerfile`, `docker-compose.yml`, `README.md`, `docs/operations/local-development.md`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: verified local startup implementation.

- [ ] **Step 1: Run targeted tests**

Run:

```bash
pytest tests/test_startup_entrypoints.py tests/test_runner.py tests/test_docker_compose_config.py tests/test_startup_docs.py -v
```

Expected: PASS.

- [ ] **Step 2: Run full test suite**

Run:

```bash
pytest tests/ -v
```

Expected: PASS.

- [ ] **Step 3: Run repository validation**

Run:

```bash
bash scripts/validate-repository.sh
```

Expected: exits 0.

- [ ] **Step 4: Smoke test Python startup without keeping the server running**

Run:

```bash
PORT=8765 python -m app
```

Expected log lines:

```text
Initializing database schema on
Started RQ worker
Starting API at http://0.0.0.0:8765 (docs: /docs)
```

Stop with `Ctrl+C` after confirming logs. If PostgreSQL or Redis is not running locally, record that the smoke check requires local services and use Task 5 Step 5 as the dependency-provisioned smoke check.

- [ ] **Step 5: Smoke test Docker startup**

Run:

```bash
docker compose up --build
```

Expected log lines from the `app` service:

```text
Initializing database schema on postgres:5432/translation
Started RQ worker
Starting API at http://0.0.0.0:8000 (docs: /docs)
```

Open `http://127.0.0.1:8000/docs` and verify the Swagger UI loads.

- [ ] **Step 6: Stop Docker stack**

Run:

```bash
docker compose down
```

Expected: containers stop and the `postgres_data` volume remains.

- [ ] **Step 7: Commit validation fixes if any were required**

If Step 1 through Step 6 required code or doc edits, commit only those files:

```bash
git add app/runner.py Dockerfile docker-compose.yml README.md docs/operations/local-development.md pyproject.toml
git commit -m "fix: stabilize unified local startup"
```

If no files changed, skip this commit.

---

## Final Acceptance

- `python -m app` is the documented local Python startup entrypoint.
- `global-backend` is not exposed as a console startup command.
- `scripts/init_db.py` is removed.
- Raw `uvicorn app.main:app` is not documented as a project startup command.
- `docker compose up --build` starts PostgreSQL, Redis, and the app.
- Docker app container runs `python -m app`.
- `/docs` loads after Python startup when local PostgreSQL and Redis are available.
- `/docs` loads after Docker Compose startup.
- `pytest tests/ -v` passes.
- `bash scripts/validate-repository.sh` passes.
