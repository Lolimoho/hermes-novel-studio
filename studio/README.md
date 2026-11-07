# Hermes Novel Studio

`studio/` 是新一代 Hermes Novel Studio 应用的独立工作区。

- `../skill/`：维护原有小说创作 Skill、参考资料、模板、语料和确定性脚本。
- `studio/`：维护 Novel Studio 产品、服务、Hermes 插件、测试和部署配置。

当前阶段：**M0 — 产品与架构基线（进行中）**。

在 M0 获得人工验收前，不创建生产代码、不锁定具体框架版本，也不进入 M1。

## 项目控制入口

- [仓库结构规划](docs/architecture/repository-structure.md)
- [里程碑与通过标准](docs/project-management/milestones.md)
- [当前里程碑状态](docs/project-management/status.md)
- [里程碑治理规则](docs/project-management/governance.md)
- [验收报告模板](docs/project-management/acceptance-template.md)
- [架构决策记录](docs/decisions/README.md)

## 规划中的产品边界

- Hermes Desktop 负责 API、模型、Profile、Skill、Memory、会话和 Kanban。
- Novel Studio 负责小说项目、设定、大纲、章节、版本、审批和自动创作策略。
- PostgreSQL 是小说正式事实与版本的权威来源。
- Hermes Agent 是创作与审查执行引擎。
- Hindsight 保存可检索的项目长期记忆，不替代正式设定。
- 所有阶段是否通过，最终由人确认。

