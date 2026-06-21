## Tasks

### Task 1: Create Application Service Layer Structure

- [x] 1.1 Create `app/application/__init__.py`
- [x] 1.2 Create `tests/application/__init__.py`

### Task 2: Implement InstallationService

- [x] 2.1 Define `InstallationNotFoundError` and `GitHubApiError` in `installation_service.py`
- [x] 2.2 Define `InstallationResponse`, `RepositoryItem`, `RepositoryListResponse` DTOs
- [x] 2.3 Implement `InstallationService.__init__(github_client: GitHubAppClient)`
- [x] 2.4 Implement `InstallationService.verify_installation(installation_id: int) -> InstallationResponse`
- [x] 2.5 Implement `InstallationService.list_repositories(installation_id: int) -> RepositoryListResponse`

### Task 3: Implement TranslationTaskService

- [x] 3.1 Define `UnsupportedLanguageError` in `translation_task_service.py`
- [x] 3.2 Define `TranslationTaskRequest` DTO
- [x] 3.3 Implement `TranslationTaskService.__init__(task_runner: TaskRunner)`
- [x] 3.4 Implement `TranslationTaskService.create_task(request: TranslationTaskRequest) -> TaskResult`

### Task 4: Write InstallationService Tests (Red)

- [x] 4.1 Create `tests/application/test_installation_service.py`
- [x] 4.2 Test `verify_installation` success case
- [x] 4.3 Test `verify_installation` raises `InstallationNotFoundError` on ValueError
- [x] 4.4 Test `verify_installation` raises `GitHubApiError` on RuntimeError
- [x] 4.5 Test `list_repositories` success case
- [x] 4.6 Test `list_repositories` raises `InstallationNotFoundError` on ValueError

### Task 5: Write TranslationTaskService Tests (Red)

- [x] 5.1 Create `tests/application/test_translation_task_service.py`
- [x] 5.2 Test `create_task` success case
- [x] 5.3 Test `create_task` raises `UnsupportedLanguageError` for invalid language
- [x] 5.4 Test `create_task` delegates to TaskRunner

### Task 6: Refactor Controllers (Green)

- [x] 6.1 Refactor `app/api/installations.py` to use InstallationService
- [x] 6.2 Refactor `app/api/tasks.py` to use TranslationTaskService
- [x] 6.3 Verify existing API tests still pass

### Task 7: Final Validation

- [x] 7.1 Run `pytest tests/application/ -v` → 9 passed
- [x] 7.2 Run `pytest tests/api/ -v` → 20 passed
- [x] 7.3 Verify controllers are thin (no business logic)
