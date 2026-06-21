# Database Schema

PostgreSQL DDL for `global-backend` persistence. Aligned with ORM models in `app/models/`.

## Tables

| Table | Purpose |
| --- | --- |
| `installation_accounts` | GitHub App installation cache |
| `translation_tasks` | Translation job lifecycle and results |
| `translation_files` | Per-file status within a task |

## Apply

```bash
psql postgresql://postgres:postgres@localhost:5432/global_backend -f db/schema/postgresql.sql
```

Or use the connection string from `.env` (remove the `+psycopg` driver suffix):

```bash
psql "${DATABASE_URL//+psycopg/}" -f db/schema/postgresql.sql
```

Create the database first if needed:

```bash
createdb global_backend
```

## Notes

- `translation_tasks.files` and `translation_tasks.mappings` store JSON as `TEXT`.
- `translation_files.task_id` references `translation_tasks.task_id` logically; no foreign key constraint.
- Tests use in-memory SQLite via SQLAlchemy `create_all`, not this file.
