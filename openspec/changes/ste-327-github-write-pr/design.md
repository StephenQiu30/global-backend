# Design: GitHub 分支、文件写入与 PR 创建

## Architecture

GitHub write operations live in `GitHubAppClient` class. Task runner calls high-level methods. PR body generation is a pure function tested separately.

## State Flow

1. Translation completes for all files → in-memory results ready
2. `create_branch()` → branch created from default branch SHA
3. `put_file()` × N → translated files written to branch
4. `build_translation_pr_body()` → PR description generated
5. `create_pull_request()` → PR created or reused
6. Task result saved with PR URL

## Failure Paths

- Translation failure before step 2: no GitHub write happens, task marked `failed`
- Branch creation failure: task marked `failed`, no file write attempted
- File write failure: task marked `failed`, no PR created
- PR creation failure: task marked `failed`, branch may exist but has no PR

## Contracts

- `GitHubAppClient` methods accept `installation_id` and repo `full_name`
- All methods are synchronous (first version)
- `httpx.Client` used for GitHub REST API calls
- JWT created per-request using `PyJWT`

## Rollback Impact

- No database to roll back
- Created branches can be manually deleted
- Half-created PRs are prevented by the two-phase design (translate all, then write all)
