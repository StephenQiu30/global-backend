## DTO 模块 (`app/dto/`)

### Requirement 1: DTO 包结构

系统 SHALL 提供 `app/dto/` 包，入参类名以 `Request` 结尾。

### Requirement 8: 控制器导入规范

控制器 SHALL 从 `app/dto/` 导入所有请求模型，从 `app/vo/` 导入所有响应模型。
