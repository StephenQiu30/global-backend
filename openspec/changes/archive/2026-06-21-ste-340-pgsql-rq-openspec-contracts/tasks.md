## 1. Database Infrastructure (SDD → 后续 ticket 实现)

- [ ] 1.1 Create `app/db/` module with SQLAlchemy async engine, `AsyncSession` factory, and `Base` declarative base class
- [ ] 1.2 Configure Alembic with `alembic.ini` and `alembic/env.py` reading `DATABASE_URL`
- [ ] 1.3 Define `DATABASE_URL` environment variable contract in `app/core/config.py`

## 2. ORM Models (SDD → 后续 ticket 实现)

- [ ] 2.1 Create `app/models/` directory with `__init__.py` exporting all models
- [ ] 2.2 Define ORM Model for each domain entity (e.g., `TranslationTask`, `Repository`) using SQLAlchemy 2.x declarative mapping
- [ ] 2.3 Ensure all models inherit from `app.db.base.Base`
- [ ] 2.4 Generate initial Alembic migration script

## 3. Repository / DAO Layer (SDD → 后续 ticket 实现)

- [ ] 3.1 Create `app/repositories/` directory
- [ ] 3.2 Implement Repository class per aggregate root with CRUD methods: `get_by_id`, `list`, `create`, `update`, `delete`
- [ ] 3.3 Repositories accept `AsyncSession` via constructor injection
- [ ] 3.4 Repositories return ORM Model instances (never raw SQL results)

## 4. DTO / VO Separation (SDD → 后续 ticket 实现)

- [ ] 4.1 Create `app/dto/` directory with Pydantic BaseModel request schemas
- [ ] 4.2 Create `app/vo/` directory with Pydantic BaseModel response schemas
- [ ] 4.3 Define DTO for each controller endpoint input
- [ ] 4.4 Define VO for each controller endpoint output
- [ ] 4.5 Ensure DTO and VO are independent even when fields overlap

## 5. Controller Layer (SDD → 后续 ticket 实现)

- [ ] 5.1 Create `app/controller/` directory with per-domain controller modules
- [ ] 5.2 Each controller defines a FastAPI Router with typed endpoints
- [ ] 5.3 Controllers receive DTO as request parameters and return VO as response
- [ ] 5.4 Controllers delegate to Application Service for business logic
- [ ] 5.5 Controllers NEVER return ORM Model instances directly
- [ ] 5.6 Register controller routers in `app/main.py`

## 6. Application Service Layer (SDD → 后续 ticket 实现)

- [ ] 6.1 Ensure `app/services/` contains Application Service classes (not just helper modules)
- [ ] 6.2 Application Services coordinate Repository, Queue, and external service calls
- [ ] 6.3 Application Services define transaction boundaries
- [ ] 6.4 Application Services contain business rule validation

## 7. Queue / Worker Layer (SDD → 后续 ticket 实现)

- [ ] 7.1 Create `app/queues/` directory with RQ queue wrapper
- [ ] 7.2 Implement type-safe enqueue methods returning RQ Job IDs
- [ ] 7.3 Create `app/workers/` directory with RQ Worker entry point
- [ ] 7.4 Workers consume tasks from the `default` RQ queue
- [ ] 7.5 Workers handle success, failure, and timeout scenarios
- [ ] 7.6 Define `REDIS_URL` environment variable contract in `app/core/config.py`

## 8. Swagger / OpenAPI (SDD → 后续 ticket 实现)

- [ ] 8.1 Ensure all controllers define `summary`, `description`, and `response_model`
- [ ] 8.2 Confirm Swagger UI available at `/docs`
- [ ] 8.3 Confirm OpenAPI JSON available at `/openapi.json`
- [ ] 8.4 Request/response schemas auto-generated from Pydantic models

## 9. Migration & Validation

- [ ] 9.1 Run `bash scripts/validate-repository.sh` to confirm repository structure
- [ ] 9.2 Review OpenSpec artifacts against `docs/plans/github-translator/11-persistence-orm-rq-plan.md`
- [ ] 9.3 Confirm no production code is bundled in this SDD change
