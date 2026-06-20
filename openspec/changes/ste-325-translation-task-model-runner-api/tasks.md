## 1. Task Domain (TDD)

- [ ] 1.1 Write failing tests in `tests/domain/test_task.py` covering TaskStatus enum, Task model, TaskResult model, FileMapping model
- [ ] 1.2 Implement `TaskStatus` enum in `app/domain/task.py`
- [ ] 1.3 Implement `FileMapping` model in `app/domain/task.py`
- [ ] 1.4 Implement `Task` model in `app/domain/task.py`
- [ ] 1.5 Implement `TaskResult` model in `app/domain/task.py`
- [ ] 1.6 Verify all domain tests pass: `pytest tests/domain/test_task.py -v`

## 2. TranslationProvider Protocol (TDD)

- [ ] 2.1 Write failing tests in `tests/services/test_translation_provider_contract.py` covering protocol compliance
- [ ] 2.2 Implement `TranslationProvider` protocol in `app/services/translation_provider.py`
- [ ] 2.3 Implement `FakeTranslationProvider` in `app/services/translation_provider.py`
- [ ] 2.4 Verify provider tests pass: `pytest tests/services/test_translation_provider_contract.py -v`

## 3. TaskRunner (TDD)

- [ ] 3.1 Write failing tests in `tests/services/test_task_runner.py` covering success path, file read error, translation error, multiple files
- [ ] 3.2 Implement `TaskRunner` in `app/services/task_runner.py` with `run()` method
- [ ] 3.3 Verify runner tests pass: `pytest tests/services/test_task_runner.py -v`

## 4. Translation Task API (TDD)

- [ ] 4.1 Write failing tests in `tests/api/test_translation_tasks.py` covering success, validation errors, task failures
- [ ] 4.2 Implement request/response models in `app/api/tasks.py`
- [ ] 4.3 Implement `router` in `app/api/tasks.py` with `POST /api/translation-tasks`
- [ ] 4.4 Register router in `app/main.py`
- [ ] 4.5 Verify API tests pass: `pytest tests/api/test_translation_tasks.py -v`

## 5. Final Validation

- [ ] 5.1 Run full test suite: `pytest tests/domain/test_task.py tests/services/test_task_runner.py tests/api/test_translation_tasks.py -v`
- [ ] 5.2 Verify no test regressions
