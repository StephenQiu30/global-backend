## 1. DTO 模块创建 (TDD)

- [x] 1.1 创建 `app/dto/__init__.py`
- [x] 1.2 创建 `app/dto/installation_dto.py`，定义 `VerifyInstallationDTO`
- [x] 1.3 创建 `app/dto/translation_task_dto.py`，定义 `CreateTranslationTaskDTO` 和 `CreatePublicPreviewDTO`
- [x] 1.4 编写 `tests/dto/test_translation_task_dto.py`，覆盖 DTO 字段校验
- [x] 1.5 验证 DTO 测试通过：`pytest tests/dto/test_translation_task_dto.py -v`

## 2. VO 模块创建 (TDD)

- [x] 2.1 创建 `app/vo/__init__.py`
- [x] 2.2 创建 `app/vo/installation_vo.py`，定义 `InstallationVO`, `RepositoryItemVO`, `RepositoryListVO`
- [x] 2.3 创建 `app/vo/translation_task_vo.py`，定义 `TranslationTaskVO`, `FileMappingVO`, `PublicPreviewVO`, `FilePreviewVO`
- [x] 2.4 编写 `tests/vo/test_translation_task_vo.py`，覆盖 VO 序列化
- [x] 2.5 验证 VO 测试通过：`pytest tests/vo/test_translation_task_vo.py -v`

## 3. 控制器迁移

- [x] 3.1 修改 `app/api/installations.py`：导入 DTO/VO，移除内联模型
- [x] 3.2 修改 `app/api/tasks.py`：导入 DTO/VO，移除内联模型，添加 TaskResult → TranslationTaskVO 转换
- [x] 3.3 修改 `app/api/public_preview.py`：导入 DTO/VO，移除内联模型，添加 PublicPreviewResult → PublicPreviewVO 转换

## 4. 集成验证

- [x] 4.1 运行现有 API 测试验证无回归：`pytest tests/api/ -v`
- [x] 4.2 运行 DTO/VO 测试：`pytest tests/dto/ tests/vo/ -v`
- [x] 4.3 检查控制器导入：确认无 `app.domain` 或 `app.services` 模型导入用于响应
- [x] 4.4 运行完整测试套件：`pytest tests/ -v`
