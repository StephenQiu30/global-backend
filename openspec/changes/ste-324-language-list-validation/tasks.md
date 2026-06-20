## 1. Language Domain (TDD)

- [ ] 1.1 Write failing tests in `tests/domain/test_languages.py` covering Language model, SUPPORTED_LANGUAGES, validate_language_code, InvalidLanguageError
- [ ] 1.2 Implement `Language` model in `app/domain/languages.py`
- [ ] 1.3 Implement `SUPPORTED_LANGUAGES` constant in `app/domain/languages.py`
- [ ] 1.4 Implement `validate_language_code` function in `app/domain/languages.py`
- [ ] 1.5 Implement `InvalidLanguageError` exception in `app/domain/languages.py`
- [ ] 1.6 Verify all domain tests pass: `pytest tests/domain/test_languages.py -v`

## 2. Languages API (TDD)

- [ ] 2.1 Write failing tests in `tests/api/test_languages_api.py` covering GET /api/languages response format
- [ ] 2.2 Implement request/response models in `app/api/languages.py`
- [ ] 2.3 Implement `router` in `app/api/languages.py` with `GET /api/languages`
- [ ] 2.4 Register router in `app/main.py`
- [ ] 2.5 Verify API tests pass: `pytest tests/api/test_languages_api.py -v`

## 3. Translation Task Integration (TDD)

- [ ] 3.1 Write failing tests in `tests/api/test_translation_tasks.py` covering unsupported language rejection
- [ ] 3.2 Modify `create_translation_task` in `app/api/tasks.py` to validate language before task creation
- [ ] 3.3 Verify integration tests pass: `pytest tests/api/test_translation_tasks.py -v`

## 4. Final Validation

- [ ] 4.1 Run full test suite: `pytest tests/domain/test_languages.py tests/api/test_languages_api.py tests/api/test_translation_tasks.py -v`
- [ ] 4.2 Verify no test regressions
