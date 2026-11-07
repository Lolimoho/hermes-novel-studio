# 项目状态

最后更新：2026-09-02

## 当前状态

- 项目状态：`ACTIVE`
- 当前里程碑：`M0`
- 当前阶段：产品与架构基线
- 当前门禁状态：`IN_PROGRESS`
- 下一里程碑：`M1`（`LOCKED`）

## 里程碑看板

| 里程碑 | 版本 | 状态 | 验收日期 |
|---|---|---|---|
| M0 产品与架构基线 | baseline | `IN_PROGRESS` | — |
| M1 工程基础与数据底座 | v0.1 | `LOCKED` | — |
| M2 人工小说工作台 | v0.2 | `LOCKED` | — |
| M3 单Agent单章闭环 | v0.3 | `LOCKED` | — |
| M4 Hermes Desktop原生集成 | v0.4 | `LOCKED` | — |
| M5 多Agent协作 | v0.5 | `LOCKED` | — |
| M6 Hindsight共享记忆 | v0.6 | `LOCKED` | — |
| M7 单章受控自动创作 | v0.8 | `LOCKED` | — |
| M8 连续创作与模式切换 | v0.9 | `LOCKED` | — |
| M9 稳定发布 | v1.0 | `LOCKED` | — |

## M0工作清单

- [ ] 产品章程、范围与非目标
- [ ] 术语表
- [ ] 核心用户流程
- [ ] 系统上下文图与容器架构图
- [ ] PostgreSQL概念数据模型
- [ ] 创作阶段状态机
- [ ] 协作模式权限矩阵
- [ ] 系统职责边界
- [ ] API与事件协议草案
- [ ] 安全与密钥方案
- [ ] Skill资产接入方案
- [ ] 关键技术ADR
- [ ] M0验收报告
- [ ] 用户验收通过

## Skill 侧待办

| 事项 | 说明 | 影响 |
|---|---|---|
| 脚本重写 | 原 `init_project` / `stats` / `export` / `continuity` 四个脚本已从 Skill 剥离，其目录约定（`meta.json`、`chapters/`）与新结构（`brief/world/outline/content/tracking`）不兼容 | 工具化能力待重建，当前靠手工流程；应在 M1 之后以 Studio 服务形式实现，不回退到脚本 |
| `templates/outline.md` 缺失 | 阶段 02 手册引用该模板，但 `skill/templates/` 中不存在 | 影响 02 阶段直接执行，需补模板或修正手册引用 |
| 阶段 05 引用 `characters.md` | 05 手册写 `characters.md`，03/08 实际产出为 `tracking/characters/{角色名}.md` | 路径不一致，执行时需以 `tracking/characters/` 为准 |

## 验收证据

尚未提交M0验收。

## 状态变更记录

| 日期 | 变更 | 原因 |
|---|---|---|
| 2026-09-02 | 初始化项目治理；M0设为 `IN_PROGRESS`，M1-M9锁定 | 用户确认正式启动，并要求建立Studio结构与里程碑控制 |
| 2026-11-08 | 仓库结构落地为 `skill/` + `studio/` 双轨；Skill 内容以远程 11f6355 为方法论基准并合并本地资产 | 双轨目录正式确立；补齐 Skill 入口文档与参考资产 |

