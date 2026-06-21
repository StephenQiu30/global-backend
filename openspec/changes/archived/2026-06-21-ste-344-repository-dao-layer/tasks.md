## Task 1: TDD Red - Write failing tests for TranslationTaskRepository

**Files:**
- `tests/repositories/test_translation_task_repository.py` (新建)

**Validation:**
- `pytest tests/repositories/test_translation_task_repository.py -v` 应全部失败

**Acceptance:**
- [ ] 测试覆盖：create queued task
- [ ] 测试覆盖：update status to running/succeeded/failed
- [ ] 测试覆盖：get_by_id for existing/non-existent task
- [ ] 测试覆盖：get_file_previews for succeeded/non-succeeded task
- [ ] 测试覆盖：failed task only stores safe error info

## Task 2: TDD Green - Implement TranslationTaskRepository

**Files:**
- `app/repositories/translation_task_repository.py` (新建)

**Validation:**
- `pytest tests/repositories/test_translation_task_repository.py -v` 应全部通过

**Acceptance:**
- [ ] 实现 create 方法
- [ ] 实现 update_status 方法
- [ ] 实现 get_by_id 方法
- [ ] 实现 get_file_previews 方法
- [ ] 返回 domain/VO 友好数据

## Task 3: TDD Red - Write failing tests for InstallationAccountRepository

**Files:**
- `tests/repositories/test_installation_account_repository.py` (新建)

**Validation:**
- `pytest tests/repositories/test_installation_account_repository.py -v` 应全部失败

**Acceptance:**
- [ ] 测试覆盖：upsert new installation
- [ ] 测试覆盖：upsert existing installation (update)

## Task 4: TDD Green - Implement InstallationAccountRepository

**Files:**
- `app/repositories/installation_account_repository.py` (新建)

**Validation:**
- `pytest tests/repositories/test_installation_account_repository.py -v` 应全部通过

**Acceptance:**
- [ ] 实现 upsert 方法
- [ ] 返回 domain/VO 友好数据

## Task 5: Validation - Run full test suite

**Validation:**
- `pytest tests/ -v` 全部通过

**Acceptance:**
- [ ] 所有新增测试通过
- [ ] 现有测试不受影响
