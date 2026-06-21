## Data Schema

### installation_accounts

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| id | INTEGER | NO | autoincrement | PK |
| installation_id | INTEGER | NO | — | GitHub installation ID, unique |
| account_login | VARCHAR(255) | NO | — | GitHub account/org name |
| account_type | VARCHAR(32) | NO | — | "User" or "Organization" |
| repository_selection | VARCHAR(32) | NO | — | GitHub repository selection mode |
| created_at | TIMESTAMP | NO | now() | |
| updated_at | TIMESTAMP | NO | now() | |

Indexes:
- `ix_installation_accounts_installation_id` UNIQUE on `installation_id`

### translation_tasks

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| id | INTEGER | NO | autoincrement | PK |
| task_id | VARCHAR(36) | NO | uuid4() | Domain task ID, unique |
| installation_id | VARCHAR(64) | NO | — | GitHub installation ID |
| repository | VARCHAR(255) | NO | — | owner/repo full name |
| base_branch | VARCHAR(255) | NO | — | |
| files | TEXT | NO | — | JSON array of source file paths |
| language | VARCHAR(16) | NO | — | Target language code |
| status | VARCHAR(16) | NO | 'queued' | queued/running/succeeded/failed |
| pr_url | VARCHAR(512) | YES | — | Set on success |
| pr_number | INTEGER | YES | — | Set on success |
| mappings | TEXT | YES | — | JSON array of {source_path, target_path} |
| error_code | VARCHAR(64) | YES | — | Set on failure |
| error_message | VARCHAR(512) | YES | — | Set on failure |
| created_at | TIMESTAMP | NO | now() | |
| updated_at | TIMESTAMP | NO | now() | |

Indexes:
- `ix_translation_tasks_task_id` UNIQUE on `task_id`

## ORM Model Rules

- All models use `Mapped` type annotations (SQLAlchemy 2.x style).
- `Base` is defined in `app/models/base.py`.
- No imports from `app/domain/`, `app/controller/`, `app/services/`.
- `files` and `mappings` stored as JSON text columns.
- Status values constrained by application logic, not DB enum (allows future extension).
- Schema initialization uses `scripts/init_db.py` (`Base.metadata.create_all`), not Alembic.
