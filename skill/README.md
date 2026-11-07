# hermes-novel-studio（Skill）

全流程网文小说创作 Skill，为 Hermes Agent 设计。从创意到大纲、人物、世界、初稿、审稿、定稿、追踪，覆盖创作全生命周期。

> 这是 Hermes Novel Studio 的**创作方法论层**。产品化实现（数据库、工作台 UI、审批流、Agent 协作）在仓库的 `studio/` 目录，两者边界见 `studio/AGENTS.md`。

## 入口

从 [SKILL.md](SKILL.md) 开始。它定义八阶段流水线、权威来源分层、目录结构与加载策略。

## 结构

```text
skill/
├── SKILL.md                    # 入口：流程编排与约束
├── README.md
├── reference/
│   ├── phases/                 # 八阶段手册（01 创意 → 08 追踪）
│   ├── modules/                # 十个专项模块（开篇/转场/对话/OOC 等）
│   ├── writing-techniques.md   # 网文写作技法（743 行）
│   ├── genre-guides.md         # 分类型写作指南（280 行）
│   ├── image-prompts.md        # 配图 prompt 库（461 行）
│   ├── platform-tactics.md     # 平台发布策略（147 行）
│   └── webnovel_corpus_guide.md# 语料检索与模仿（261 行）
├── templates/                  # 项目文件模板
│   ├── brief.md                # 创意纲要
│   ├── world.md                # 世界观
│   ├── rules.md                # 风格规范
│   ├── progress.md             # 进度与伏笔台账
│   ├── character-sheet.md      # 角色卡（L1-L4 分层）
│   └── chapter.md              # 章节骨架
├── data/articles/              # 166 篇网文原文语料
├── analysis/                   # 摘录库、文风 profile、模仿索引
└── novels/                     # 项目实例（含三只小猪示例）
```

## 运行方式

本 Skill 不含可执行脚本，全部流程由 Agent 按 `SKILL.md` 与各阶段手册驱动，产物一律落盘为 Markdown。

初始化项目、统计字数、导出全本等工具化能力，属于 `studio/` 的工程范围，不在此实现。

## 项目文件约定

每个小说项目位于 `workspace/novels/{name}/`，核心文件：

- `brief.md` / `world.md` / `outline.md` / `rules.md`：静态权威
- `tracking/progress.md`、`tracking/characters/`：动态权威
- `content/chXX-draft.md`：草稿；`content/chXX.md`：定稿
