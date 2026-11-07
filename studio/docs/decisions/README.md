# 架构决策记录（ADR）

影响系统边界、数据兼容性、外部依赖、安全或长期维护成本的决策必须记录为ADR。

文件命名：

```text
0001-short-decision-title.md
0002-next-decision.md
```

每份ADR至少包含：

- 状态：Proposed / Accepted / Superseded / Rejected；
- 背景；
- 决策；
- 备选方案；
- 正面影响；
- 风险和代价；
- 兼容性与迁移影响；
- 复审条件。

M0预计至少确认以下决策：

1. Studio宿主形态与Hermes Desktop插件边界；
2. 前后端和共享契约的技术栈；
3. PostgreSQL权威数据模型与Markdown关系；
4. Hermes/Kanban执行状态与Studio工作流状态边界；
5. Hindsight项目共享记忆隔离策略；
6. 人工审批不可绕过的权限模型。

## 已提交

| 编号 | 标题 | 状态 | 覆盖 |
|---|---|---|---|
| [0001](0001-host-form-and-ui-architecture.md) | 宿主形态与 UI 架构 | Proposed | 上述第 1、2 项，部分第 6 项 |

