# Novel Studio · 验证 Demo

用于验证 M0 概念模型与核心交互是否成立的**最小可运行原型**。

不是生产代码，不进入 M1 的工程骨架。M1 应从本 demo 复用**模型结论**，不复用实现。

## 验证什么

| # | 假设 | 在哪里看 |
|---|---|---|
| 1 | 稿件必须拆成三个正交维度（状态 / 版本 / 来源），否则建模会错 | 候选稿生成后章节仍是「待写」，接受后才变「草稿」 |
| 2 | 定稿不是另存文件，而是某条版本被批准 | 版本列表里同一版从候选 → 草稿 → 定稿，行不变 |
| 3 | 人工审批门不可被 AI 绕过 | 有阻断意见时定稿返回 409 |
| 4 | 小说工作台应以文档为中心，AI 是阶段执行器 | 每页只有一个主动作：生成蓝图 / 写这一章 / 审稿 / 定稿 |
| 5 | 版本可回溯且不覆盖历史 | 回退任意版本 → 生成新版本，旧版保留 |

## 技术栈

- 后端：FastAPI + SQLAlchemy + **SQLite**（schema 按 PostgreSQL 设计）
- 前端：React 19 + TypeScript + Vite，纯 CSS 纸墨风格
- Agent：`MockAdapter`，按契约实现 `generate_plans` / `generate_draft` / `review`

> 没有 Docker 和 PostgreSQL 也能跑，这是选 SQLite 的唯一原因。换库时只改 `app/db.py` 的连接串。

## 启动

后端（终端 1）：

```bash
cd studio/demo/api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端（终端 2）：

```bash
cd studio/demo/web
npm install
npm run dev
```

打开 http://127.0.0.1:5173

## 演示路径

1. **书房** → 新建作品，填标题、类型、章数、每章字数、一句话前提
2. **设定** → 补世界观，保存
3. **架构** → 加主角（L4）与对手（L3），填 Want / Lie
4. **蓝图** → 生成 10 章，逐章可改目标、冲突、钩子
5. **正文** → 打开第 1 章
   - 「AI 写稿」→ 出现**候选稿**（章节状态仍是待写）
   - 「接受为草稿」→ 状态变草稿，版本 +1
   - 「审稿」→ 出 4-5 条意见，可采纳/忽略
   - 「定稿」→ 状态变定稿
   - 版本列表可回退任意版本
6. **运行** → 每一次 AI 动作的耗时与产物

## 已验证的结果

用接口脚本跑通完整链路（含失败路径）：

```text
0. 建作品 201
1. 生成蓝图 200，3 章
2. 写第 1 章 201：候选稿 1261 字，source=ai，accepted_at=None
3. 未接受时状态：not_started（候选不改变状态）
4. 接受候选 200：draft
5. 审稿 200：4 条
6. 定稿 200：finalized
7. 审批门：短稿审出 1 条阻断意见 → 定稿 409「还有 1 条阻断级意见未处理」
   处理阻断意见后 → 200 finalized
8. 版本链 v1(ai) v2(human) → 回退生成 v3，状态 draft
9. 运行记录 5 条，全部 succeeded
```

## 已知边界（刻意不做）

- **没有鉴权与多用户**：单机验证用，任何人打开即全部权限。
- **没有并发控制**：两人同改一章会互相覆盖，正式版需要 `If-Match` 或版本号乐观锁。
- **没有真实模型**：`MockAdapter` 按蓝图字段拼文本，只为验证数据流与字数。
- **没有文件落盘**：全部进库，不生成 `chXX-draft.md`，Markdown 双向同步留到 M1 后。
- **没有流式输出**：动作是同步等待，正式版应走 SSE。
- **候选稿不可丢弃**：只能接受，不能删除（缺一个 `discard` 接口）。

## 目录

```text
studio/demo/
├── api/
│   ├── app/
│   │   ├── models.py          # 8 张表，与概念模型一一对应
│   │   ├── schemas.py
│   │   ├── db.py              # SQLite 连接，换库只改这里
│   │   ├── agent/
│   │   │   ├── base.py        # AgentAdapter 契约
│   │   │   └── mock.py        # 唯一实现
│   │   └── routers/
│   │       ├── projects.py    # 作品 / 角色 / 卷
│   │       ├── chapters.py    # 蓝图 / 正文 / 审稿 / 定稿 / 回退
│   │       └── runs.py
│   └── data/demo.db           # 运行时生成，已忽略
└── web/
    └── src/
        ├── pages/             # 书房 / 设定 / 架构 / 蓝图 / 正文 / 运行
        ├── api.ts
        └── types.ts
```

## 与正式架构的差距

| 项 | demo | 正式 |
|---|---|---|
| 数据库 | SQLite 单文件 | PostgreSQL + 迁移 |
| Agent | Mock 同步调用 | Hermes adapter + SSE |
| 鉴权 | 无 | 用户 / 权限 / 审批人 |
| 并发 | 无 | 乐观锁或版本校验 |
| 文件 | 只进库 | Markdown 双向同步 |
| 审计 | run 表 | run + approval + 审计日志 |
