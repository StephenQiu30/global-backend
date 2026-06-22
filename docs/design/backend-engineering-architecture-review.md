# Backend Engineering Architecture Review

> Companion document to the PRD 11 persistence plan
> (`docs/plans/github-translator/11-persistence-orm-rq-plan.md`).

## Goal

Provide a repository-local architecture guide so future backend changes follow
the same enterprise-style layered structure. This is not a platform manifesto;
it is an actionable reference for contributors working in `global-backend`.

## Target Module Layout

```text
app/
  controller/          # FastAPI controllers — the only HTTP interface layer
  domain/              # Pure business logic, enums, value rules
  dto/                 # Inbound request schemas (XxxRequest)
  vo/                  # Outbound response schemas (XxxVO)
  models/              # SQLAlchemy ORM models mapped to PgSQL tables
  repositories/        # Database access boundary (SQLAlchemy sessions)
  db/                  # Engine, session factory, schema initialization
  services/            # Business orchestration + external clients (GitHub, OpenAI)
  queues/              # Redis/RQ queue adapters
  workers/             # RQ job entrypoints
  core/                # Settings, errors, shared infrastructure
```

## Module Responsibilities

### `controller/`

FastAPI `APIRouter` definitions. Controllers are the **only** HTTP interface
source of truth — no endpoint definitions should exist outside this layer.

Each controller file:
- Declares route handlers with explicit `tags`, `response_model`, and
  `responses` metadata.
- Validates inbound data using Request DTOs from `app/dto/`.
- Returns outbound data as VOs from `app/vo/`.
- Delegates business logic to a service in `app/services/`.
- Contains no direct database queries, no ORM imports, and no inline Pydantic
  request/response models.

**Naming:** Files: `{resource}_controller.py`.

### `services/`

Business orchestration and infrastructure-facing clients.

Orchestration services (e.g. `TranslationTaskService`) coordinate domain logic,
repositories, queue adapters, and external clients. Infrastructure clients
(e.g. `GitHubAppClient`, `OpenAITranslationProvider`) wrap external APIs.

Each orchestration service:
- Accepts primitive arguments or domain objects as input.
- Calls repositories for persistence, clients for external calls, and queue
  adapters for async work.
- Returns VOs or domain objects.
- Contains no HTTP or FastAPI imports.

**Naming:** `{Resource}Service` (e.g. `TranslationTaskService`). Files:
`{resource}_service.py` or `{system}.py` for clients.

### `domain/`

Pure business logic: Pydantic models, enums, validation rules, and value
objects that are not tied to HTTP or database concerns.

Current contents include `TaskStatus`, `Task`, `TaskResult`, `RepositoryRef`,
`Language`, and markdown path rules.

**Rule:** Domain must not import from SQLAlchemy, FastAPI, `controller/`,
`dto/`, `vo/`, `models/`, or `repositories/`.

### `dto/`

Inbound request schemas used by controllers for input validation.

**Naming:** `{Action}{Resource}Request` (e.g. `CreateTranslationTaskRequest`,
`VerifyInstallationRequest`). Files: `{resource}.py`.

**Rule:** DTOs are Pydantic `BaseModel` subclasses. They must not import ORM
models or database session objects.

### `vo/`

Outbound response and view schemas returned by controllers.

**Naming:** `{Resource}VO` (e.g. `TranslationTaskCreateVO`,
`TranslationTaskStatusVO`). Files: `{resource}_vo.py`.

**Rule:** VOs are Pydantic `BaseModel` subclasses. Controllers must never
return ORM model instances directly — always convert to a VO first.

### `models/`

SQLAlchemy 2.x ORM models mapped to PostgreSQL tables. Each model file
defines one `Mapped` class with column definitions, indexes, and table name.

`Base` (DeclarativeBase) lives in `app/models/base.py`.

**Naming:** `{Resource}Model` (e.g. `TranslationTaskModel`). Files:
`{resource}.py`.

**Rule:** Models must not import from `controller/`, `dto/`, `vo/`, or
`services/`.

### `repositories/`

Database access boundary using SQLAlchemy async sessions. Each repository
wraps queries and mutations for one aggregate or table.

**Naming:** `{Resource}Repository` (e.g. `TranslationTaskRepository`). Files:
`{resource}_repository.py`.

**Rule:** Repositories may depend on `models/` and `db/`. They must not
depend on `controller/`, `dto/`, or `vo/`. Methods are named after product
actions (e.g. `create`, `get_by_id`), not generic CRUD.

### `db/`

SQLAlchemy engine configuration, async session factory, and schema init.

Current files:
- `engine.py` — async engine factory.
- `session.py` — `get_async_session()` async generator.
- `schema.py` — `init_schema()` using `Base.metadata.create_all`.

Schema is initialized by the unified local process entrypoint
`app.runner:main` during `python -m app` startup, not by a separate script.

### `queues/`

Redis/RQ queue adapters. Each adapter wraps `enqueue()` for one job type.

**Naming:** `{Resource}Queue` (e.g. `TranslationTaskQueue`). Files:
`{resource}_queue.py`.

### `workers/`

RQ job entrypoints. Each worker function receives a job ID, loads the record
via a repository, and delegates to a service.

**Naming:** `{resource}_jobs.py` (e.g. `translation_jobs.py`).

### `core/`

Shared infrastructure: `Settings` (pydantic-settings), `ApiResponseVO[T]`
generic response envelope, `ErrorCode` enum, `AppException` with centralized
exception handlers, `TraceIdMiddleware`, and the `openapi.py` helper for
shared OpenAPI error response metadata.

## Dependency Rules

```text
controller ──→ dto, vo, services
services ──→ domain, repositories, queues, (external clients)
repositories ──→ models, db
models ──→ base (DeclarativeBase only)
domain ──→ (no framework imports)
workers ──→ services, queues
queues ──→ (Redis/RQ client only)
```

**Forbidden directions:**
- `models` must NOT depend on `controller`, `dto`, `vo`, or `services`.
- `domain` must NOT depend on SQLAlchemy, FastAPI, `models/`, `repositories/`,
  `controller/`, `dto/`, or `vo/`.
- `repositories` must NOT depend on `controller`, `dto/`, or `vo/`.
- `controller` must NOT import ORM models or database sessions.

## Where to Add New Features

| If you are adding...           | Put it in...         | Example file                          |
|--------------------------------|----------------------|---------------------------------------|
| A new API endpoint             | `controller/`        | `translation_task_controller.py`      |
| Business orchestration logic   | `services/`          | `translation_task_service.py`         |
| Business rules or enums        | `domain/`            | `task.py`, `languages.py`             |
| Inbound request validation     | `dto/`               | `translation_task.py`                 |
| Outbound response shape        | `vo/`                | `translation_task_vo.py`              |
| A new database table           | `models/`            | `translation_task.py`                 |
| Database query logic           | `repositories/`      | `translation_task_repository.py`      |
| An external API client         | `services/`          | `github_app.py`                       |
| A background job queue adapter | `queues/`            | `translation_task_queue.py`         |
| A background job entrypoint    | `workers/`           | `translation_jobs.py`                 |
| App configuration              | `core/config.py`     | Add `Settings` field                  |

## Controllers Are the Only HTTP Interface

All HTTP endpoint definitions MUST live under `app/controller/`. No endpoint
definitions should exist outside this layer.

**Why:** A single source of truth for HTTP interfaces makes Swagger
documentation, API testing, and interface review predictable.

## Global Response Contract

All API responses use the `ApiResponseVO[T]` envelope defined in
`app/core/response.py`:

```json
{
  "code": "SUCCESS",
  "message": "OK",
  "data": "<payload>",
  "trace_id": "<uuid>"
}
```

Error responses use the same envelope with `data: null`:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "<detail>",
  "data": null,
  "trace_id": "<uuid>"
}
```

### Error Handling

- `AppException` (in `app/core/exceptions.py`) is the structured application
  exception carrying `code: ErrorCode`, `message`, `http_status`, and
  `retryable`.
- Centralized exception handlers convert `AppException`, `RequestValidationError`,
  `StarletteHTTPException`, and unhandled `Exception` into the global envelope.
- Controllers SHALL NOT maintain local error-to-status mappings. They raise
  `AppException` and let the centralized handler produce the response.
- `ErrorCode` is an 11-member uppercase string enum. Each code maps to an HTTP
  status via `ERROR_CODE_HTTP_STATUS` in `app/core/response.py`.

### OpenAPI Error Response Helper

`app/core/openapi.py` provides `common_error_responses(*codes)` to generate
OpenAPI `responses` metadata for route decorators. This avoids repeating
per-endpoint error VO classes:

```python
from app.core.openapi import common_error_responses
from app.core.response import ErrorCode

@router.post(
    "/endpoint",
    response_model=ApiResponseVO[MyVO],
    responses=common_error_responses(
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.INTERNAL_ERROR,
    ),
)
```

Pre-built tuples (`VALIDATION_ERRORS`, `NOT_FOUND_ERRORS`, `SERVER_ERRORS`)
cover common endpoint patterns.

## Swagger / OpenAPI Requirements

Every new controller endpoint must satisfy these requirements:

1. **Tags:** Each router must declare `tags=[...]` grouping related endpoints.
2. **Response model:** Every endpoint must declare `response_model` using a VO.
3. **Error responses:** Every endpoint must declare `responses` metadata using
   `common_error_responses()` for the error codes it can raise.
4. **Operation ID:** Configure stable `operation_id` generation.
5. **No ORM models in responses:** Always convert to a VO.
6. **Documentation endpoints:** Swagger UI at `/docs` and OpenAPI JSON at
   `/openapi.json` must remain available.

## Naming Conventions Summary

| Layer          | Class suffix   | File suffix        | Example                              |
|----------------|----------------|--------------------|--------------------------------------|
| Controller     | (functions)    | `_controller.py`   | `create_translation_task`            |
| Service        | `Service`      | `_service.py`      | `TranslationTaskService`             |
| Domain         | (none)         | `.py`              | `Task`, `TaskStatus`                 |
| DTO            | `Request`      | `.py`              | `CreateTranslationTaskRequest`       |
| VO             | `VO`           | `_vo.py`           | `TranslationTaskCreateVO`            |
| ORM Model      | `Model`        | `.py`              | `TranslationTaskModel`               |
| Repository     | `Repository`   | `_repository.py`   | `TranslationTaskRepository`          |
| Queue Adapter  | `Queue`        | `_queue.py`        | `TranslationTaskQueue`               |
| Worker         | (function)     | `_jobs.py`         | `translation_jobs.py`                |

## Explicit Non-Goals

These are intentionally not part of this architecture:

- **No `app/application/` layer.** Orchestration lives in `app/services/`.
- **No `app/api/` layer.** HTTP lives only in `app/controller/`.
- **No Alembic migrations (current phase).** Schema initialization is owned by
  `app.runner:main` for local startup.
- **No frontend work.** This document covers backend structure only.
- **No full authentication system.** Auth decisions are deferred.
- **No generic repository base class.** Add only when real duplication appears.
- **No multi-queue prioritization.** One RQ queue until the first path works.
- **No dependency injection framework.** FastAPI `Depends()` is sufficient.
- **No event bus or workflow engine.** Keep orchestration in services.
