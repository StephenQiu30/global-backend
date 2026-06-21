CREATE TABLE IF NOT EXISTS installation_accounts (
    id SERIAL PRIMARY KEY,
    installation_id INTEGER NOT NULL UNIQUE,
    account_login VARCHAR(255) NOT NULL,
    account_type VARCHAR(32) NOT NULL,
    repository_selection VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS translation_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL UNIQUE,
    installation_id VARCHAR(64) NOT NULL,
    repository VARCHAR(255) NOT NULL,
    base_branch VARCHAR(255) NOT NULL,
    files TEXT NOT NULL,
    language VARCHAR(16) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'queued',
    pr_url VARCHAR(512),
    pr_number INTEGER,
    mappings TEXT,
    error_code VARCHAR(64),
    error_message VARCHAR(512),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS translation_files (
    id VARCHAR(32) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL,
    source_path VARCHAR(500) NOT NULL,
    target_path VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_translation_files_task_id ON translation_files (task_id);
