# Unified Local Startup Design

## Goal

Unify local startup for `global-backend` around one Python main entrypoint and
one Docker Compose command. The result should let developers start the backend
without remembering separate database initialization, API, and worker commands.

## Current Context

The repository already has an emerging unified entrypoint:

- `app/__main__.py` allows `python -m app`.
- `pyproject.toml` exposes `global-backend = "app.runner:main"`.
- `app/runner.py` initializes the database schema, starts an RQ worker child
  process, and starts Uvicorn.
- `README.md` and `docs/operations/local-development.md` already describe
  `python -m app` as the local startup command.

The missing piece is a Docker one-command local development path. There is no
accepted `Dockerfile` or `docker-compose.yml` in the current repository state.

## Chosen Approach

Use **local main plus Docker Compose all-in-one**.

Local startup:

```bash
python -m app
```

Installed console startup:

```bash
global-backend
```

Docker startup:

```bash
docker compose up --build
```

This keeps the mental model small: one Python entrypoint and one Docker command.

## Architecture

### Python Main Entrypoint

`app.runner:main` is the single process-level entrypoint for local development.
It owns this sequence:

1. Load `Settings`.
2. Initialize database schema from ORM metadata.
3. Start one RQ worker child process for the configured queue.
4. Start the FastAPI app through Uvicorn.
5. On API shutdown, terminate and join the worker child process.

`app/__main__.py` should stay thin and only call `app.runner:main`.

`app/main.py` remains the FastAPI application factory and must not become the
process orchestration layer.

### Docker Compose

Docker Compose is the local dependency manager. It should start:

- `postgres`: PostgreSQL database.
- `redis`: Redis broker for RQ.
- `app`: the backend container running the same `python -m app` entrypoint.

The app container should depend on `postgres` and `redis` and use container
network URLs:

- `DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/translation`
- `REDIS_URL=redis://redis:6379/0`
- `RQ_QUEUE_NAME=translation`

The compose path is for local development, not production deployment.

## Components

### Dockerfile

The Dockerfile should:

- Use a Python 3.12+ base image.
- Install project dependencies with `pip install -e ".[dev]"` or equivalent.
- Copy the application and docs needed for local development.
- Expose port `8000`.
- Run `python -m app` as the default command.

### docker-compose.yml

The compose file should:

- Define `postgres`, `redis`, and `app` services.
- Persist PostgreSQL data in a named volume.
- Map API port `8000:8000`.
- Provide local-development environment values for database and Redis.
- Avoid production-only concerns such as replicas, external networks, or
  multi-profile deployment topology.

### Documentation

Update README and operations docs so the startup choices are explicit:

- Local Python: `python -m app`
- Installed command: `global-backend`
- Docker: `docker compose up --build`
- Stop Docker stack: `docker compose down`
- Reset Docker database: `docker compose down -v`
- API docs: `http://127.0.0.1:8000/docs`

## Error Handling

- If `DATABASE_URL`, `REDIS_URL`, or `RQ_QUEUE_NAME` are missing, startup should
  fail early with the existing settings validation rather than silently choosing
  hidden defaults.
- Docker Compose should include healthchecks for PostgreSQL and Redis, and the
  app service should depend on those services becoming healthy. The Python main
  entrypoint does not need its own retry loop in the first version.
- If the RQ worker child exits unexpectedly, local startup should surface the
  process logs. The first version does not need a supervisor or restart policy
  inside Python.

## Testing And Validation

Automated:

```bash
pytest tests/ -v
bash scripts/validate-repository.sh
```

Startup smoke checks:

```bash
python -m app
docker compose up --build
```

Manual acceptance:

- `GET /docs` loads after local Python startup.
- `GET /docs` loads after Docker Compose startup.
- Startup logs show database initialization, worker startup, and API startup.

## Non-Goals

- No production deployment design.
- No separate Docker profiles for API and worker in the first version.
- No Kubernetes, Helm, Procfile, or process manager.
- No replacement of SQLAlchemy schema initialization with Alembic migrations in
  this startup design.
- No frontend container.

## Configuration Decisions

- `docker-compose.yml` should load `.env` for GitHub/OpenAI secrets when the
  file exists.
- Compose should override infrastructure URLs for container networking:
  `DATABASE_URL` points at `postgres`, and `REDIS_URL` points at `redis`.
- `RQ_QUEUE_NAME` should default to `translation` in compose.
