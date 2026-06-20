# global-backend

`global-backend` 的项目协作规范已从
[`StephenQiu30/stephen-cladue`](https://github.com/StephenQiu30/stephen-cladue)
同步到本仓库。

本目录当前用于沉淀后端项目的 Claude Agent 协作规则、Symphony/Linear
执行契约、OpenSpec/SDD 规范层、TDD/RAG 验证门禁和 Git/PR 收口要求。

## 规范入口

1. `CLAUDE.md`：长期稳定的 Claude 协作规范，包含 MVP、SDD、TDD、RAG、角色协作和交付输出要求。
2. `CLAUDE.local.md`：`global-backend` 的项目局部规范，用于记录路径、命令、环境约束和临时约定。
3. `WORKFLOW.md`：Symphony 风格的 Linear ticket 调度契约与 per-ticket Agent SOP。
4. `.claude/agents/`：PM、Explorer、Builder、Tester、Reporter 五类角色定义。
5. `.claude/skills/`：Harness、Superpowers、OpenSpec、Linear、Git 收口和验证技能。
6. `openspec/`：仓库内 SDD 规范层，保存长期规格与后续变更提案。
7. `docs/`：PRD、计划、设计、验收和运维文档骨架。
8. `.github/`：PR 模板与 CI 结构检查。

## 核心门禁

1. 需求、计划和验收遵循 SMART。
2. 涉及长期行为、接口、数据模型、状态机、队列或权限的任务先走 OpenSpec/SDD。
3. 核心逻辑修改默认 TDD，保留 Red -> Green -> Refactor 证据。
4. RAG 指红绿测试门禁，不是检索增强生成。
5. 完成任务前执行匹配范围的测试、lint、构建或可复现手工验证。
6. 提交使用中文说明，类型限定为 `test:`、`docs:`、`impl:`、`feat:`、`chore:`、`refactor:`。
7. PR 进入 Human Review 前必须补齐 Workpad、验证证据、PR 描述和反馈 sweep。

## 本地验证

```bash
scripts/validate-repository.sh
```

## 规范来源

本规范骨架来自 `StephenQiu30/stephen-cladue`，并已按 `global-backend`
项目身份保留本地化入口。后续如需同步模板更新，应先比对差异，只导入共享治理规则，避免覆盖项目特有文档。
