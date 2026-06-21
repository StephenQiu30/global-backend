# PRD 11 Persistence Engineering Linear Task Breakdown

> This document decomposes
> `docs/plans/github-translator/11-persistence-orm-rq-plan.md` into
> execution-ready Linear issue bodies. Each task is scoped to one deliverable or
> one tightly related change set.

## Task 1: Define OpenSpec Contract For PgSQL, SQLAlchemy, RQ, And Layering

## Goal
- Establish the approved SDD contract for PgSQL persistence, SQLAlchemy ORM,
  Redis/RQ queueing, controller-based APIs, DTO/VO separation, and Swagger docs.

## Task Description
- Background: Persistence, queueing, and enterprise-style layering affect
  long-lived backend architecture and must be specified before implementation.
- Expected change: Create an OpenSpec change that defines PgSQL as the database,
  SQLAlchemy 2.x + Alembic as ORM/migration tooling, Redis/RQ as queueing, and
  `controller/application/domain/dto/vo/models/repositories/db/queues/workers`
  as the target backend structure.
- OpenSpec impact: New change under
  `openspec/changes/add-pgsql-rq-persistence/`.

## Scope Boundaries
- In scope: OpenSpec proposal, specs, design, tasks for persistence, queueing,
  controller Swagger requirements, and module boundaries.
- Out of scope: Production code, dependency installation, database migrations,
  frontend changes, Linear issue creation.
- Explicit non-goals: No custom MyBatis clone, no workflow engine, no generic
  repository framework, no multi-queue strategy.

## Acceptance Criteria
- OpenSpec artifacts explicitly require PostgreSQL, SQLAlchemy 2.x, Alembic,
  Redis/RQ, `app/controller/`, DTO, VO, ORM Model, Repository/DAO, Application
  Service, Queue, and Worker boundaries.
- OpenSpec artifacts define that Swagger/OpenAPI is generated from controller
  definitions and remains available at `/docs` and `/openapi.json`.
- OpenSpec artifacts state that ORM Models must never be returned directly from
  controller responses.

## Validation
- Automated: Run the repository OpenSpec validation command if available, plus
  `bash scripts/validate-repository.sh`.
- Manual: Review the OpenSpec change against
  `docs/plans/github-translator/11-persistence-orm-rq-plan.md`.
- Agent Review focus: Confirm no implementation work is bundled into this SDD
  task and no scope beyond approved architecture is introduced.

## Deliverables
- `openspec/changes/add-pgsql-rq-persistence/proposal.md`
- `openspec/changes/add-pgsql-rq-persistence/specs.md`
- `openspec/changes/add-pgsql-rq-persistence/design.md`
- `openspec/changes/add-pgsql-rq-persistence/tasks.md`

---

## Task 2: Add Enterprise Persistence And Queue Configuration

## Goal
- Make PgSQL, Redis, and RQ configurable through project settings without
  hard-coded infrastructure values in controllers or services.

## Task Description
- Background: The backend currently has no accepted database or queue runtime
  configuration.
- Expected change: Add dependencies and settings for SQLAlchemy, Alembic,
  psycopg, Redis, and RQ.
- OpenSpec impact: Implement the configuration portion of
  `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: `pyproject.toml`, `app/core/config.py`, config tests.
- Out of scope: ORM models, migrations, repositories, API behavior changes.
- Explicit non-goals: No Docker Compose setup unless separately approved; no
  production secret management system.

## Acceptance Criteria
- Settings expose `database_url`, `redis_url`, and `rq_queue_name`.
- Default values are local-development friendly and overridable by environment.
- Tests prove env vars override defaults.
- No controller, repository, or worker hard-codes PgSQL/Redis connection values.

## Validation
- Automated: `pytest tests/test_config.py -v`
- Manual: Inspect `.env.example` if updated and confirm no real secrets are
  included.
- Agent Review focus: Confirm config is minimal and does not introduce unused
  environment variables.

## Deliverables
- Updated `pyproject.toml`
- Updated `app/core/config.py`
- Updated or added `tests/test_config.py`
- Optional `.env.example` entries without secrets

---

## Task 3: Create SQLAlchemy ORM Models And Alembic Migration

## Goal
- Represent persistent translation data with SQLAlchemy ORM Models and a PgSQL
  migration that can create the required tables.

## Task Description
- Background: Task history, installation account metadata, and translated file
  preview metadata need durable database tables.
- Expected change: Add SQLAlchemy 2.x typed ORM models and Alembic migration for
  installation accounts, translation tasks, and translation files.
- OpenSpec impact: Implement the persistence schema portion of
  `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: SQLAlchemy base/session setup, ORM models, Alembic setup, migration,
  model tests.
- Out of scope: Repository methods, API endpoints, RQ workers.
- Explicit non-goals: No generic base model hierarchy beyond shared SQLAlchemy
  base; no extra audit tables; no user auth tables.

## Acceptance Criteria
- `InstallationAccountModel`, `TranslationTaskModel`, and
  `TranslationFileModel` map to PgSQL tables.
- Tables include required fields for installation metadata, task status/result,
  and translated file metadata.
- Indexes exist for `task_id`, `installation_id`, and recent task lookup.
- Alembic migration can create the schema from an empty database.

## Validation
- Automated: `pytest tests/db/test_models.py -v`
- Automated: Run Alembic upgrade against a test PgSQL database when available.
- Manual: Review migration SQL for missing nullable constraints and indexes.
- Agent Review focus: Ensure ORM Models are persistence-only and do not import
  DTO/VO/controller modules.

## Deliverables
- `app/db/base.py`
- `app/db/session.py`
- `app/models/installation_account_model.py`
- `app/models/translation_task_model.py`
- `app/models/translation_file_model.py`
- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/*_add_translation_persistence.py`
- `tests/db/test_models.py`

---

## Task 4: Split DTO And VO Schemas From Controllers

## Goal
- Make inbound request DTOs and outbound response VOs explicit, so controllers
  do not own schema definitions and ORM Models are never exposed as API output.

## Task Description
- Background: Existing FastAPI routers define request/response models inline.
  The target structure follows a Spring Boot inspired controller/service style.
- Expected change: Move request schemas into `app/dto/` and response schemas
  into `app/vo/`, keeping domain rules in `app/domain/`.
- OpenSpec impact: Implement DTO/VO separation in
  `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: DTO and VO modules for installation verification, translation task
  creation/status, and translated file previews.
- Out of scope: Database models, repositories, RQ workers, frontend components.
- Explicit non-goals: No DTO/VO duplication for endpoints not touched by this
  persistence change unless required by controller migration.

## Acceptance Criteria
- Controllers import request models from `app/dto/`.
- Controllers return response models from `app/vo/`.
- DTO names end with `DTO`; VO names end with `VO`.
- ORM Models are not imported by controllers for response serialization.

## Validation
- Automated:
  `pytest tests/dto/test_translation_task_dto.py tests/vo/test_translation_task_vo.py -v`
- Manual: Inspect controller imports after migration.
- Agent Review focus: Confirm DTO/VO are not being used as SQLAlchemy models and
  domain validation remains in domain modules.

## Deliverables
- `app/dto/installation_dto.py`
- `app/dto/translation_task_dto.py`
- `app/vo/installation_vo.py`
- `app/vo/translation_task_vo.py`
- `tests/dto/test_translation_task_dto.py`
- `tests/vo/test_translation_task_vo.py`

---

## Task 5: Add Repository/DAO Layer For Installation And Translation Records

## Goal
- Centralize database access behind focused repositories so raw SQLAlchemy
  session usage does not leak into controllers or application services.

## Task Description
- Background: Persistence should be testable and isolated from HTTP routing.
- Expected change: Add repositories for installation account metadata and
  translation task/file persistence using SQLAlchemy sessions.
- OpenSpec impact: Implement Repository/DAO boundary in
  `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: Repository classes and tests for saving/loading installation
  accounts, task records, failed task state, and translated file previews.
- Out of scope: API routes, worker execution, broad generic base repository.
- Explicit non-goals: No dynamic query DSL; no pagination framework; no
  cross-entity repository abstraction until duplication proves it is needed.

## Acceptance Criteria
- `InstallationAccountRepository` can upsert verified installation metadata.
- `TranslationTaskRepository` can create queued tasks, update success/failure,
  read task status/result, and read file preview metadata.
- Failed task persistence stores only safe error code/message.
- Repositories return domain/VO-friendly data and do not return raw ORM Models
  to controllers.

## Validation
- Automated: `pytest tests/repositories/test_translation_task_repository.py -v`
- Manual: Inspect transaction/session usage for clear ownership.
- Agent Review focus: Confirm repository methods map to product actions and do
  not become an open-ended abstraction layer.

## Deliverables
- `app/repositories/installation_account_repository.py`
- `app/repositories/translation_task_repository.py`
- `tests/repositories/test_translation_task_repository.py`

---

## Task 6: Add Application Services For Installation And Translation Tasks

## Goal
- Move business orchestration out of HTTP controllers and into testable
  application services.

## Task Description
- Background: Controllers should behave like Spring Boot controllers: thin HTTP
  adapters that delegate to services.
- Expected change: Add application services that coordinate DTO input, domain
  validation, repositories, GitHub clients, translation providers, and queue
  submission.
- OpenSpec impact: Implement Application Service boundary in
  `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: Installation verification service and translation task service.
- Out of scope: UI, new translation provider behavior, broad refactor of
  unrelated GitHub client code.
- Explicit non-goals: No dependency injection framework; use FastAPI dependency
  wiring unless evidence shows it is insufficient.

## Acceptance Criteria
- `InstallationService` verifies GitHub installation and persists safe account
  metadata.
- `TranslationTaskService` creates task records and maps results/status to VOs.
- Service tests can run without HTTP TestClient.
- Controllers contain no business orchestration beyond request/response mapping.

## Validation
- Automated: `pytest tests/application/test_translation_task_service.py -v`
- Manual: Inspect controllers after migration for thinness.
- Agent Review focus: Check that application services enforce OpenSpec
  boundaries and do not reach directly into HTTP request objects.

## Deliverables
- `app/application/installation_service.py`
- `app/application/translation_task_service.py`
- `tests/application/test_translation_task_service.py`

---

## Task 7: Move API Interfaces Into Controller Modules And Add Swagger Docs

## Goal
- Put all HTTP endpoint definitions under `app/controller/` and ensure
  Swagger/OpenAPI documents DTOs, VOs, tags, operation IDs, and error responses.

## Task Description
- Background: The user wants interface files defined in controller modules,
  similar to Java Spring Boot controllers, with Swagger interface docs.
- Expected change: Move endpoint declarations from `app/api/` into
  `app/controller/` and configure FastAPI OpenAPI metadata.
- OpenSpec impact: Implement controller and Swagger requirements in
  `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: Controller modules, route registration in `app/main.py`, OpenAPI
  tags, response models, documented error responses, stable operation IDs.
- Out of scope: Frontend generated clients, external Swagger hosting,
  hand-written OpenAPI YAML.
- Explicit non-goals: No duplicate endpoint definitions in both `api` and
  `controller`; after migration, controller is source of truth.

## Acceptance Criteria
- All HTTP endpoint declarations live under `app/controller/`.
- Swagger UI remains available at `/docs`.
- OpenAPI JSON remains available at `/openapi.json`.
- Each endpoint has a tag, stable operation ID, success `response_model`, and
  expected error `responses`.
- Controller responses use VOs, not ORM Models.

## Validation
- Automated: `pytest tests/controller/test_openapi_docs.py -v`
- Manual: Open `/docs` in a local server if runtime validation is requested.
- Agent Review focus: Confirm OpenAPI docs are generated from code and route
  duplication did not occur.

## Deliverables
- `app/controller/installation_controller.py`
- `app/controller/repository_controller.py`
- `app/controller/language_controller.py`
- `app/controller/translation_task_controller.py`
- `app/controller/public_preview_controller.py`
- Updated `app/main.py`
- `tests/controller/test_openapi_docs.py`

---

## Task 8: Add Minimal Redis/RQ Translation Queue Boundary

## Goal
- Submit translation task IDs to Redis/RQ through one queue adapter and one
  worker entrypoint.

## Task Description
- Background: Translation work should move toward background execution without
  introducing a custom workflow engine.
- Expected change: Add a minimal RQ queue adapter and worker job that loads a
  task by ID and delegates to application service execution.
- OpenSpec impact: Implement queue boundary in `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: One queue adapter, one queue name, one worker job function, tests
  proving enqueue behavior.
- Out of scope: Multiple priority queues, retry policy, scheduled jobs,
  dashboard, worker deployment automation.
- Explicit non-goals: No task orchestration framework and no event bus.

## Acceptance Criteria
- `TranslationTaskQueue.enqueue(task_id)` enqueues exactly one RQ job.
- Worker entrypoint accepts `task_id` and delegates to the application service.
- Queue name comes from config.
- Tests do not require a live Redis unless explicitly marked as integration.

## Validation
- Automated: `pytest tests/queues/test_translation_task_queue.py -v`
- Manual: Optional live Redis enqueue smoke test if local Redis is available.
- Agent Review focus: Confirm the queue layer stays minimal and does not
  introduce unapproved retries or scheduling.

## Deliverables
- `app/queues/translation_task_queue.py`
- `app/workers/translation_jobs.py`
- `tests/queues/test_translation_task_queue.py`

---

## Task 9: Integrate Persistent Task Submission, Status, And File Preview APIs

## Goal
- Let API callers create a translation task, receive a task ID, poll task
  status/result, and fetch translated file preview metadata from persisted data.

## Task Description
- Background: User information, translation task records, and translated file
  metadata must survive after request completion.
- Expected change: Wire controllers to application services, repositories, and
  queue adapter for installation verification and translation task lifecycle.
- OpenSpec impact: Implement API integration for `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: Installation verification persistence, translation task creation,
  queued status, task status endpoint, file preview endpoint.
- Out of scope: Frontend UI, generated API client, full auth/session model.
- Explicit non-goals: No synchronous fallback path unless already accepted by
  existing behavior and documented in OpenSpec.

## Acceptance Criteria
- Successful installation verification persists safe account metadata.
- `POST /api/translation-tasks` returns a task ID and queued/running state.
- `GET /api/translation-tasks/{task_id}` returns persisted task status/result.
- `GET /api/translation-tasks/{task_id}/file-previews` returns persisted
  translated file metadata.
- Unknown task IDs return documented `task_not_found` errors.

## Validation
- Automated: `pytest tests/api/test_persistence_api.py -v`
- Manual: Inspect `/openapi.json` for the new endpoints and schemas.
- Agent Review focus: Check consistency across DTO, VO, service, repository,
  controller, and OpenSpec artifacts.

## Deliverables
- Updated controller modules
- Updated application services
- Updated repositories
- `tests/api/test_persistence_api.py`

---

## Task 10: Document Backend Engineering Architecture Rules

## Goal
- Provide a repository-local architecture guide so future backend changes follow
  the same controller/service/repository/DTO/VO/Model structure.

## Task Description
- Background: The project is moving from MVP layout to an enterprise-style
  backend structure inspired by Spring Boot.
- Expected change: Add a concise architecture review/rules document under
  `docs/design/`.
- OpenSpec impact: Documentation companion to `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: Module responsibilities, dependency rules, naming conventions,
  Swagger requirements, non-goals.
- Out of scope: Code changes, generated diagrams, frontend architecture.
- Explicit non-goals: No broad platform manifesto; keep the guide actionable for
  this repository.

## Acceptance Criteria
- Document explains `controller`, `application`, `domain`, `dto`, `vo`,
  `models`, `repositories`, `db`, `queues`, and `workers`.
- Document states dependency rules and where new features should add files.
- Document states controllers are the only HTTP interface source of truth.
- Document states Swagger/OpenAPI requirements for future controller endpoints.

## Validation
- Automated: `bash scripts/validate-repository.sh`
- Manual: Read the document against this task breakdown and the PRD 11 plan.
- Agent Review focus: Confirm the document does not contradict OpenSpec or add
  unapproved architecture scope.

## Deliverables
- `docs/design/backend-engineering-architecture-review.md`

---

## Task 11: Final Validation And Agent Review Handoff

## Goal
- Prove the persistence engineering change is complete, verified, and ready for
  Agent Review without boundary drift.

## Task Description
- Background: The full change spans OpenSpec, architecture, ORM models,
  repositories, services, controllers, Swagger docs, and queueing.
- Expected change: Run targeted tests, repository validation, and summarize
  implementation-to-spec evidence.
- OpenSpec impact: Verify and prepare archive path for
  `add-pgsql-rq-persistence`.

## Scope Boundaries
- In scope: Validation commands, evidence summary, OpenSpec task completion,
  Agent Review notes.
- Out of scope: New feature work, unrelated cleanup, frontend changes.
- Explicit non-goals: No test expansion beyond affected behavior unless a real
  regression is discovered.

## Acceptance Criteria
- Targeted tests pass for config, models, DTO, VO, repositories, application
  services, queues, controllers/OpenAPI, and persistence API.
- `bash scripts/validate-repository.sh` passes.
- Any live PgSQL/Redis checks that cannot run are documented with exact missing
  service reason.
- Agent Review has clear focus areas and changed files.

## Validation
- Automated:
  `pytest tests/test_config.py tests/db/test_models.py tests/dto/test_translation_task_dto.py tests/vo/test_translation_task_vo.py tests/repositories/test_translation_task_repository.py tests/application/test_translation_task_service.py tests/queues/test_translation_task_queue.py tests/controller/test_openapi_docs.py tests/api/test_persistence_api.py -v`
- Automated: `bash scripts/validate-repository.sh`
- Manual: Review `/docs` and `/openapi.json` if a local server is started.
- Agent Review focus: Verify OpenSpec compliance, no duplicate API/controller
  endpoints, no ORM Model leakage to VO responses, no overdesigned queue or
  repository framework.

## Deliverables
- Validation evidence in PR/Workpad
- Completed OpenSpec task checklist
- Agent Review notes for boundary and Swagger verification
