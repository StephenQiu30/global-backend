## 1. Language Domain (TDD)

- [x] 1.1 Write failing tests in `tests/domain/test_languages.py` covering Language model, SUPPORTED_LANGUAGES, validate_language_code, InvalidLanguageError
- [x] 1.2 Implement `Language` model in `app/domain/languages.py`
- [x] 1.3 Implement `SUPPORTED_LANGUAGES` constant in `app/domain/languages.py`
- [x] 1.4 Implement `validate_language_code` function in `app/domain/languages.py`
- [x] 1.5 Implement `InvalidLanguageError` exception in `app/domain/languages.py`
- [x] 1.6 Verify all domain tests pass: `pytest tests/domain/test_languages.py -v`

## 2. Languages API (TDD)

- [x] 2.1 Write failing tests in `tests/api/test_languages_api.py` covering GET /api/languages response format
- [x] 2.2 Implement request/response models in `app/api/languages.py`
- [x] 2.3 Implement `router` in `app/api/languages.py` with `GET /api/languages`
- [x] 2.4 Register router in `app/main.py`
- [x] 2.5 Verify API tests pass: `pytest tests/api/test_languages_api.py -v`

## 3. Translation Task Integration (TDD)

- [x] 3.1 Write failing tests in `tests/api/test_translation_tasks.py` covering unsupported language rejection
- [x] 3.2 Modify `create_translation_task` in `app/api/tasks.py` to validate language before task creation
- [x] 3.3 Verify integration tests pass: `pytest tests/api/test_translation_tasks.py -v`

## 4. Final Validation

- [x] 4.1 Run full test suite: `pytest tests/domain/test_languages.py tests/api/test_languages_api.py tests/api/test_translation_tasks.py -v`
- [x] 4.2 Verify no test regressions
