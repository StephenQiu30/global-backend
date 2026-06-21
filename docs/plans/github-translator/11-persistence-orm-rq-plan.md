# PRD 11 Persistence ORM And RQ Implementation Plan

> **Scope note:** This is a task plan only. Do not modify application code until
> the plan is reviewed and approved.

**Goal:** Add enterprise-style durable persistence for user-facing GitHub
installation account information, translation task records, translated file
metadata, and task status lookup using PgSQL. Use Redis/RQ as the background
task queue boundary, and refactor the backend toward explicit DTO, VO, Domain,
ORM Model, Service, Repository/DAO, and Worker boundaries.

**Architecture:** Keep the implementation enterprise-shaped but not oversized:
FastAPI controllers handle HTTP and DTO validation; services own business
orchestration; repositories/DAOs own SQLAlchemy persistence; ORM Models map
PgSQL tables; VO objects shape API responses; translation work is submitted to
one RQ queue. Swagger/OpenAPI documentation is generated from controller
definitions. No custom workflow engine and no frontend implementation in this
backend plan.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, Redis, RQ, pytest.

## Enterprise ORM Direction

Python does not have a one-to-one MyBatis equivalent in the mainstream FastAPI
stack. Enterprise Python backends most commonly use SQLAlchemy for ORM/database
work, with Alembic for migrations. The practical choices are:

1. **SQLAlchemy 2.x ORM/Core - recommended**
   - Mature, widely used, works well with PgSQL.
   - ORM models cover normal CRUD; Core/text queries stay available when SQL
     needs to be explicit, which gives a MyBatis-like escape hatch.
   - Pairs cleanly with Alembic for schema migrations.

2. **SQLModel**
   - Friendlier Pydantic-style model ergonomics on top of SQLAlchemy.
   - Good for small apps, but adds another abstraction layer and can become
     limiting when query control matters.

3. **Peewee**
   - Lightweight ORM.
   - Smaller ecosystem than SQLAlchemy and less standard for FastAPI PgSQL
     services.

**Decision:** Use SQLAlchemy 2.x directly. It is the least surprising choice for
PgSQL and keeps SQL control available without building a MyBatis-style mapper
layer ourselves.

## Engineering Layering Target

The backend should move from a compact MVP layout to a clear enterprise service
layout. The goal is explicit responsibilities, not extra ceremony.

```text
app/
  controller/          # FastAPI controllers only, like Spring Boot controllers
  application/         # use-case services / orchestration
  domain/              # domain objects, value rules, enums
  dto/                 # request DTOs and command/query input schemas
  vo/                  # response VOs returned by API
  models/              # SQLAlchemy ORM models mapped to PgSQL tables
  repositories/        # database access using SQLAlchemy sessions
  db/                  # engine/session/base configuration
  services/            # infrastructure-facing services that already exist
  queues/              # Redis/RQ queue adapters
  workers/             # RQ worker job entrypoints
  core/                # settings, errors, shared infrastructure
```

### Naming Rules

- **DTO:** inbound request or application command data. Examples:
  `CreateTranslationTaskDTO`, `VerifyInstallationDTO`.
- **VO:** outbound view/response shape. Examples:
  `TranslationTaskVO`, `TranslationFilePreviewVO`, `InstallationAccountVO`.
- **Domain:** business concepts and rules that are not tied to HTTP or DB.
  Examples: `TaskStatus`, language validation, file path mapping rules.
- **ORM Model:** SQLAlchemy mapped class, one class per table. Examples:
  `TranslationTaskModel`, `TranslationFileModel`, `InstallationAccountModel`.
- **Repository/DAO:** database access boundary. Examples:
  `TranslationTaskRepository`, `InstallationAccountRepository`.
- **Application Service:** business orchestration that coordinates repositories,
  GitHub clients, translation provider, and queue. Example:
  `TranslationTaskService`.
- **Queue Adapter:** minimal RQ wrapper. Example:
  `TranslationTaskQueue`.
- **Worker:** RQ entrypoint that loads by ID and delegates to application
  service. Example: `run_translation_task(task_id)`.
- **Controller:** HTTP interface layer. All API endpoints live here, similar to
  Spring Boot `@RestController`. Examples:
  `TranslationTaskController`, `InstallationController`.

### Dependency Rules

- `controller` may depend on `dto`, `vo`, and `application`.
- `application` may depend on `domain`, `repositories`, `queues`, and existing
  external services.
- `repositories` may depend on `models` and `db`.
- `models` must not depend on `controller`, `dto`, `vo`, or services.
- `domain` must stay framework-light and must not depend on SQLAlchemy/FastAPI.
- `workers` may depend on `application` and queue/job configuration only.

This gives clear DTO/VO/Model separation without creating a Java-style package
tree that is larger than the current product needs.

## Global Constraints

- Database MUST be PostgreSQL.
- Message queue MUST be Redis/RQ.
- ORM MUST be SQLAlchemy 2.x with Alembic migrations.
- DTO, VO, ORM Model, Domain, Repository/DAO, Application Service, Queue, and
  Worker responsibilities MUST be separated by module.
- All HTTP endpoint definitions MUST live under `app/controller/`.
- Swagger/OpenAPI docs MUST be generated from controller definitions and remain
  available through FastAPI's documentation endpoints.
- Keep persistence code focused on accepted records only:
  installation account metadata, translation tasks, translated file metadata.
- Do not store GitHub tokens, private keys, model raw payloads, or stack traces.
- Do not add frontend work unless a separate frontend plan is approved.
- Do not introduce broad repository abstractions, event buses, or workflow
  orchestration without explicit approval.

---

## Task 1: OpenSpec / Contract Update

**Repo:** `global-backend`

**Files:**
- Create: `openspec/changes/add-pgsql-rq-persistence/proposal.md`
- Create: `openspec/changes/add-pgsql-rq-persistence/specs.md`
- Create: `openspec/changes/add-pgsql-rq-persistence/design.md`
- Create: `openspec/changes/add-pgsql-rq-persistence/tasks.md`

**Steps:**
- [ ] Define PgSQL as the only database target.
- [ ] Define Redis/RQ as the only queue target.
- [ ] Define SQLAlchemy 2.x + Alembic as the ORM/migration target.
- [ ] Define DTO/VO/Domain/ORM Model/Repository/Application Service boundaries.
- [ ] Define `app/controller/` as the only HTTP endpoint layer.
- [ ] Define Swagger/OpenAPI documentation requirements for all controllers.
- [ ] Specify persisted entities and fields.
- [ ] Specify non-goals: no full auth system, no workflow engine, no frontend.
- [ ] Validate the change artifacts against current specs.

**Acceptance:**
- The persistence and queue behavior is explicit before code changes begin.

## Task 2: Dependencies And Configuration

**Repo:** `global-backend`

**Files:**
- Modify: `pyproject.toml`
- Modify: `app/core/config.py`
- Test: `tests/test_config.py`

**Steps:**
- [ ] Add `sqlalchemy`, `alembic`, `psycopg`, `redis`, and `rq`.
- [ ] Add `database_url`, `redis_url`, and `rq_queue_name` settings.
- [ ] Write failing tests for env var loading.
- [ ] Run: `pytest tests/test_config.py -v`.

**Acceptance:**
- Runtime configuration can point to PgSQL and Redis without hard-coded local
  values in service code.

## Task 3: SQLAlchemy Models And Migration

**Repo:** `global-backend`

**Files:**
- Create: `app/db/base.py`
- Create: `app/db/session.py`
- Create: `app/models/installation_account_model.py`
- Create: `app/models/translation_task_model.py`
- Create: `app/models/translation_file_model.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/*_add_translation_persistence.py`
- Test: `tests/db/test_models.py`

**Steps:**
- [ ] Model `installation_accounts`.
- [ ] Model `translation_tasks`.
- [ ] Model `translation_files`.
- [ ] Add indexes for `task_id`, `installation_id`, and recent task lookup.
- [ ] Write tests that inspect model table names and required columns.
- [ ] Run: `pytest tests/db/test_models.py -v`.

**Acceptance:**
- PgSQL schema can be created through Alembic and is represented by SQLAlchemy
  models.

## Task 4: DTO / VO Boundary

**Repo:** `global-backend`

**Files:**
- Create: `app/dto/installation_dto.py`
- Create: `app/dto/translation_task_dto.py`
- Create: `app/vo/installation_vo.py`
- Create: `app/vo/translation_task_vo.py`
- Test: `tests/dto/test_translation_task_dto.py`
- Test: `tests/vo/test_translation_task_vo.py`

**Steps:**
- [ ] Move inbound FastAPI request models out of routers into `app/dto/`.
- [ ] Move outbound response/view models into `app/vo/`.
- [ ] Keep existing domain rules in `app/domain/`.
- [ ] Do not expose SQLAlchemy ORM models from API responses.
- [ ] Run: `pytest tests/dto/test_translation_task_dto.py tests/vo/test_translation_task_vo.py -v`.

**Acceptance:**
- Routers use DTOs for input and VOs for output.
- ORM Models are never returned directly from API routes.

## Task 5: Repository / DAO Layer

**Repo:** `global-backend`

**Files:**
- Create: `app/repositories/installation_account_repository.py`
- Create: `app/repositories/translation_task_repository.py`
- Test: `tests/repositories/test_translation_task_repository.py`

**Steps:**
- [ ] Write failing tests for saving installation account metadata.
- [ ] Write failing tests for saving successful task result and file records.
- [ ] Write failing tests for saving failed task result with safe error fields.
- [ ] Implement SQLAlchemy session usage in repositories/DAOs.
- [ ] Keep methods named after product actions; avoid generic base repositories.
- [ ] Run: `pytest tests/repositories/test_translation_task_repository.py -v`.

**Acceptance:**
- Persistence code is centralized in repositories and does not leak into API
  routers.

## Task 6: Application Service Layer

**Repo:** `global-backend`

**Files:**
- Create: `app/application/translation_task_service.py`
- Create: `app/application/installation_service.py`
- Test: `tests/application/test_translation_task_service.py`

**Steps:**
- [ ] Move task creation orchestration out of `app/api/tasks.py`.
- [ ] Coordinate DTO -> domain/service -> repository -> VO mapping.
- [ ] Keep existing GitHub and translation provider code as infrastructure
  services unless a focused extraction is needed.
- [ ] Run: `pytest tests/application/test_translation_task_service.py -v`.

**Acceptance:**
- API routers become thin controllers.
- Business flow is testable without HTTP.

## Task 7: Redis/RQ Queue Boundary

**Repo:** `global-backend`

**Files:**
- Create: `app/queues/translation_task_queue.py`
- Create: `app/workers/translation_jobs.py`
- Test: `tests/queues/test_translation_task_queue.py`

**Steps:**
- [ ] Write failing test that task submission enqueues one RQ job.
- [ ] Implement a minimal `TranslationTaskQueue.enqueue(task_id)` wrapper.
- [ ] Implement one worker entry function that loads the task by ID and runs
  existing translation orchestration.
- [ ] Do not add retries, schedules, priorities, dashboards, or multiple queues
  in the first pass.
- [ ] Run: `pytest tests/queues/test_translation_task_queue.py -v`.

**Acceptance:**
- Translation execution can be handed to Redis/RQ through one clear boundary.

## Task 8: Controller Layer And Swagger Documentation

**Repo:** `global-backend`

**Files:**
- Create: `app/controller/installation_controller.py`
- Create: `app/controller/translation_task_controller.py`
- Modify: `app/main.py`
- Test: `tests/controller/test_openapi_docs.py`

**Steps:**
- [ ] Move all HTTP endpoint declarations from `app/api/` into
  `app/controller/`.
- [ ] Keep controllers thin: validate DTO, call application service, return VO.
- [ ] Add OpenAPI tags for each controller group:
  `installations`, `repositories`, `languages`, `translation-tasks`,
  `public-preview`.
- [ ] Add `response_model` for every successful endpoint.
- [ ] Add `responses` metadata for expected 400/403/404/422/500-class errors.
- [ ] Configure stable OpenAPI `operation_id` generation so generated clients do
  not churn unexpectedly.
- [ ] Ensure FastAPI Swagger UI remains available at `/docs` and OpenAPI JSON at
  `/openapi.json`.
- [ ] Write tests that assert `/openapi.json` contains controller tags,
  operation IDs, success schemas, and documented error responses.
- [ ] Run: `pytest tests/controller/test_openapi_docs.py -v`.

**Acceptance:**
- All interface files are under `app/controller/`.
- Swagger/OpenAPI accurately documents request DTOs, response VOs, tags, and
  error responses.
- No controller returns ORM Models directly.

## Task 9: API Integration

**Repo:** `global-backend`

**Files:**
- Modify: `app/controller/installation_controller.py`
- Modify: `app/controller/translation_task_controller.py`
- Modify: `app/main.py`
- Test: `tests/api/test_persistence_api.py`

**Steps:**
- [ ] Persist verified installation account metadata after GitHub verification.
- [ ] Create a queued translation task record on `POST /api/translation-tasks`.
- [ ] Enqueue the task ID through RQ.
- [ ] Add `GET /api/translation-tasks/{task_id}` for task status/result.
- [ ] Add `GET /api/translation-tasks/{task_id}/file-previews` for translated
  file metadata.
- [ ] Run: `pytest tests/api/test_persistence_api.py -v`.

**Acceptance:**
- API callers can submit a task, poll its status, and preview translated file
  metadata after completion.

## Task 10: Package Structure Review

**Repo:** `global-backend`

**Files:**
- Create: `docs/design/backend-engineering-architecture-review.md`

**Steps:**
- [ ] Document final module boundaries.
- [ ] Document the Spring Boot inspired controller/service/repository shape.
- [ ] Document DTO/VO/Domain/ORM Model dependency rules.
- [ ] Document Swagger/OpenAPI requirements for future controllers.
- [ ] Document where new features should add files.
- [ ] Document what is intentionally not added to avoid overdesign.

**Acceptance:**
- Future agents can follow the same structure without guessing.

## Task 11: Validation

**Repo:** `global-backend`

**Commands:**

```bash
pytest tests/test_config.py tests/db/test_models.py tests/dto/test_translation_task_dto.py tests/vo/test_translation_task_vo.py tests/repositories/test_translation_task_repository.py tests/application/test_translation_task_service.py tests/queues/test_translation_task_queue.py tests/controller/test_openapi_docs.py tests/api/test_persistence_api.py -v
bash scripts/validate-repository.sh
```

**Acceptance:**
- Targeted tests pass.
- Repository validation passes.
- Any skipped live PgSQL/Redis checks are documented with exact missing service
  reason.

## Explicit Non-Goals

- No frontend UI work in this plan.
- No full user authentication system.
- No custom MyBatis clone or mapper DSL.
- No generic repository base class unless duplication appears after real code is
  written.
- No multi-queue prioritization or retry policy until the first RQ path works.
- No dependency injection framework unless FastAPI dependencies become
  insufficient after implementation evidence.
- No duplicate endpoint definitions in both `api` and `controller`; after
  migration, `controller` is the HTTP interface source of truth.
