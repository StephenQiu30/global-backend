## Requirement: InstallationAccountRepository MUST Support Upsert

`InstallationAccountRepository` SHALL 提供 `upsert` 方法，用于保存或更新验证过的安装账户元数据。

### Scenario: Upsert new installation account
- GIVEN 一个尚未存在的 installation_id
- WHEN 调用 upsert 方法传入 installation_id、account_login、account_type、repository_selection
- THEN 记录被创建
- AND 返回保存后的数据

### Scenario: Upsert existing installation account
- GIVEN 一个已存在的 installation_id
- WHEN 调用 upsert 方法传入更新后的 account_login 或其他字段
- THEN 记录被更新（不创建新记录）
- AND 返回更新后的数据

## Requirement: InstallationAccountRepository MUST Return Domain Data

`InstallationAccountRepository` SHALL 返回 domain/VO 友好数据，不返回原始 ORM Model。

### Scenario: Return type is domain model
- WHEN 调用任何 InstallationAccountRepository 方法
- THEN 返回值 SHALL 是 Pydantic model 或 dataclass
- AND 返回值 SHALL NOT 是 SQLAlchemy ORM Model

## Requirement: TranslationTaskRepository MUST Create Queued Tasks

`TranslationTaskRepository` SHALL 提供 `create` 方法，用于创建状态为 queued 的翻译任务。

### Scenario: Create a new translation task
- GIVEN 有效的 installation_id、repository、base_branch、files、language
- WHEN 调用 create 方法
- THEN 任务记录被创建
- AND 状态为 queued
- AND 返回包含 task_id 的任务数据

## Requirement: TranslationTaskRepository MUST Update Task Status

`TranslationTaskRepository` SHALL 提供 `update_status` 方法，用于更新任务状态。

### Scenario: Update task to running
- GIVEN 一个 queued 状态的任务
- WHEN 调用 update_status 方法设置状态为 running
- THEN 任务状态被更新为 running

### Scenario: Update task to succeeded
- GIVEN 一个 running 状态的任务
- WHEN 调用 update_status 方法设置状态为 succeeded，并传入 pr_url、pr_number、mappings
- THEN 任务状态被更新为 succeeded
- AND 结果数据被保存

### Scenario: Update task to failed
- GIVEN 一个 running 状态的任务
- WHEN 调用 update_status 方法设置状态为 failed，并传入 error_code、error_message
- THEN 任务状态被更新为 failed
- AND 仅保存安全的 error_code 和 error_message（不保存堆栈或敏感信息）

## Requirement: TranslationTaskRepository MUST Read Task Status/Result

`TranslationTaskRepository` SHALL 提供 `get_by_id` 方法，用于读取任务状态和结果。

### Scenario: Get existing task
- GIVEN 一个已存在的任务
- WHEN 调用 get_by_id 方法
- THEN 返回任务的完整数据，包括状态、结果（如有）、错误信息（如有）

### Scenario: Get non-existent task
- GIVEN 一个不存在的 task_id
- WHEN 调用 get_by_id 方法
- THEN 返回 None

## Requirement: TranslationTaskRepository MUST Read File Preview Metadata

`TranslationTaskRepository` SHALL 提供 `get_file_previews` 方法，用于读取翻译后的文件预览元数据。

### Scenario: Get file previews for succeeded task
- GIVEN 一个 succeeded 状态的任务，包含文件映射
- WHEN 调用 get_file_previews 方法
- THEN 返回文件映射列表（source_path, target_path）

### Scenario: Get file previews for non-succeeded task
- GIVEN 一个非 succeeded 状态的任务
- WHEN 调用 get_file_previews 方法
- THEN 返回空列表

## Requirement: Failed Task MUST Store Only Safe Error Info

失败任务的持久化 SHALL 仅存储安全的 error_code 和 error_message。

### Scenario: Error fields are safe
- WHEN 任务失败并持久化
- THEN error_code SHALL 是预定义的错误码之一（如 file_read_error、translation_error、unknown_error）
- AND error_message SHALL NOT 包含堆栈跟踪、token、secret 或内部实现细节
