## Tasks

### Task 1: Create Application Service Layer Structure

- [ ] 1.1 Create `app/application/__init__.py`
- [ ] 1.2 Create `tests/application/__init__.py`

### Task 2: Implement InstallationService

- [ ] 2.1 Define `InstallationNotFoundError` and `GitHubApiError` in `installation_service.py`
- [ ] 2.2 Define `InstallationResponse`, `RepositoryItem`, `RepositoryListResponse` DTOs
- [ ] 2.3 Implement `InstallationService.__init__(github_client: GitHubAppClient)`
- [ ] 2.4 Implement `InstallationService.verify_installation(installation_id: int) -> InstallationResponse`
- [ ] 2.5 Implement `InstallationService.list_repositories(installation_id: int) -> RepositoryListResponse`

### Task 3: Implement TranslationTaskService

- [ ] 3.1 Define `UnsupportedLanguageError` in `translation_task_service.py`
- [ ] 3.2 Define `TranslationTaskRequest` DTO
- [ ] 3.3 Implement `TranslationTaskService.__init__(task_runner: TaskRunner)`
- [ ] 3.4 Implement `TranslationTaskService.create_task(request: TranslationTaskRequest) -> TaskResult`

### Task 4: Write InstallationService Tests (Red)

- [ ] 4.1 Create `tests/application/test_installation_service.py`
- [ ] 4.2 Test `verify_installation` success case
- [ ] 4.3 Test `verify_installation` raises `InstallationNotFoundError` on ValueError
- [ ] 4.4 Test `verify_installation` raises `GitHubApiError` on RuntimeError
- [ ] 4.5 Test `list_repositories` success case
- [ ] 4.6 Test `list_repositories` raises `InstallationNotFoundError` on ValueError

### Task 5: Write TranslationTaskService Tests (Red)

- [ ] 5.1 Create `tests/application/test_translation_task_service.py`
- [ ] 5.2 Test `create_task` success case
- [ ] 5.3 Test `create_task` raises `UnsupportedLanguageError` for invalid language
- [ ] 5.4 Test `create_task` delegates to TaskRunner

### Task 6: Refactor Controllers (Green)

- [ ] 6.1 Refactor `app/api/installations.py` to use InstallationService
- [ ] 6.2 Refactor `app/api/tasks.py` to use TranslationTaskService
- [ ] 6.3 Verify existing API tests still pass

### Task 7: Final Validation

- [ ] 7.1 Run `pytest tests/application/ -v`
- [ ] 7.2 Run `pytest tests/api/ -v`
- [ ] 7.3 Verify controllers are thin (no business logic)
