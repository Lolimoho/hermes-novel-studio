---
name: hermes-novel-studio
description: "全流程网文小说创作工作室，从灵感到完本。八阶段流水线：创意孵化 → 架构设计 → 人物工坊 → 世界构建 → 初稿写作 → 修订审稿 → 定稿输出 → 追踪管理。适用场景：(1) 从零创作一部小说，(2) 续写/恢复中断项目，(3) 人物与世界观设计，(4) 章节审稿与修订，(5) 平台定稿适配。触发词：写小说、创作网文、开坑、大纲、人设、世界观、写第X章、审稿、定稿、更新台账、novel studio。"
version: "2.0.0"
metadata:
  category: creative-writing
  language: zh-CN
  tags: [novel, fiction, creative-writing, 网文, 小说创作, full-lifecycle]
---

# Hermes Novel Studio

全流程网文创作工作室——从灵感到完本。

本 Skill 只负责**创作方法论与流程**。工程侧（数据库、UI、审批流、多 Agent 协作）由 `studio/` 承载，两者边界见仓库根 `studio/AGENTS.md`。

---

## 一、权威来源分层

写作与审稿的一切判断，都以下列文件为准，不以对话记忆为准。

| 层级 | 文件 | 性质 |
|---|---|---|
| 静态权威 | `brief.md` `world.md` `outline.md` `rules.md` | 定义后稳定，改动需回溯已有章节 |
| 动态权威 | `tracking/progress.md` `tracking/characters/*.md` | 每章定稿后更新 |
| 草稿 | `content/chXX-draft.md` | 未定稿，可反复修改 |
| 定稿 | `content/chXX.md` | 已定稿，不静默覆盖 |

**冲突处理**：发现正文与权威不一致，先确认哪一方是权威，修正正文；若权威本身过时，先与用户确认，再同步更新权威与正文。

---

## 二、八阶段总览

| 阶段 | 名称 | 触发词 | 主要产出 | 手册 |
|---|---|---|---|---|
| 01 | 创意孵化 | 新书、开坑、有个想法 | `brief.md` | `reference/phases/01-creative-brief/` |
| 02 | 架构设计 | 大纲、卷纲、精化大纲 | `outline.md`（骨架 → 精化） | `reference/phases/02-plot-outline/` |
| 03 | 人物工坊 | 人物、角色、人设 | `tracking/characters/*.md` | `reference/phases/03-characters/` |
| 04 | 世界构建 | 世界观、设定、力量体系 | `world.md` | `reference/phases/04-worldbuilding/` |
| 05 | 初稿写作 | 写第X章、继续写、下一章 | `content/chXX-draft.md` | `reference/phases/05-drafting/` |
| 06 | 修订审稿 | 审稿、改稿、看看这章 | 修订 `chXX-draft.md` | `reference/phases/06-revision/` |
| 07 | 定稿输出 | 定稿、发布、平台格式 | `content/chXX.md` | `reference/phases/07-finalization/` |
| 08 | 追踪管理 | 更新台账、伏笔状态 | `tracking/*` | `reference/phases/08-tracking/` |

```text
主链：01 创意 → 02 骨架 → 03 人物 → 02 精化 → 04 世界 → 05 初稿 → 06 修订 → 07 定稿 → 08 追踪
回退：06 任一轮不通过 → 退回 05 改稿，改完重跑 06
```

- 02 分两轮，中间隔着 03：第一轮只出**骨架**（终点 + 卷结构 + 角色功能需求），确认后进 03；第二轮**精化**（章级大纲 + 弧线节点 + 伏笔）必须等 03 的 L4/L3 角色卡填满后回访执行。
- 04 只依赖骨架版 `outline.md`，位置可在 03 之后、02 精化前后浮动；但 05 之前必须完成。
- 06 未通过，不进入 07。07 未完成，不进入 08。

---

## 三、项目目录结构

```text
workspace/novels/{name}/
├── brief.md               # 创意纲要（01 产出，静态权威）
├── outline.md             # 卷结构与章节大纲（02 产出）
├── world.md               # 世界观与设定（04 产出）
├── rules.md               # 项目风格规范（静态权威）
├── content/
│   ├── ch01-draft.md      # 初稿（05 产出，06 修订）
│   └── ch01.md            # 定稿（07 产出）
├── tracking/
│   ├── progress.md        # 时间线、伏笔、线索（动态权威）
│   └── characters/
│       └── {角色名}.md    # 角色卡（03 产出，08 更新）
├── images/                # 配图
└── export/                # 导出产物
```

示例项目见 `novels/三只小猪（示例）/`，可作为目录与文件格式参照。

---

## 四、阶段 0：项目初始化

工具脚本已从本 Skill 剥离，初始化改为**手动建目录 + 复制模板**：

1. 创建目录：`content/`、`tracking/characters/`、`images/`、`export/`
2. 复制模板并填入占位内容：

| 模板 | 目标路径 |
|---|---|
| `templates/brief.md` | `brief.md` |
| `templates/world.md` | `world.md` |
| `templates/rules.md` | `rules.md` |
| `templates/progress.md` | `tracking/progress.md` |

`outline.md` 由 02 阶段直接生成；角色卡按 03 阶段的 `templates/character-sheet.md` 逐人创建。

**已有项目**（续写/恢复）：跳过本节，直接读 `brief.md` → `outline.md` → `tracking/progress.md` 恢复状态，再从 `content/` 中未定稿的 `-draft.md` 接续。

---

## 五、各阶段要点

### 01 创意孵化 → `brief.md`

六步线性推进：收集灵感 → 六要素讨论 → 一句话概括 → 情感引擎 → 标题候选 → 写入。核心冲突必须拆成**表层/内层/深层**三层，缺一层的方案不进入 02。任何一项用户"还没想好"，就这一项深聊，不跳过。

### 02 架构设计 → `outline.md`

两轮制，中间隔着 03。第一轮出**骨架**：故事终点、卷结构、每卷末状态（谁做了什么选择导致什么）、角色功能需求（只写功能，**禁止在此阶段设计具体人物**），确认后进 03。03 完成后回访做第二轮**精化**：逐章标题、核心剧情点、目标字数、弧线节点、伏笔衔接。三幕比例约 10-15% / 70% / 15-20%，每卷伏笔 / 回收 ≥ 2 / 1。

### 03 人物工坊 → `tracking/characters/`

按**角色层级**决定填写深度：L4 主角级（Wound → Lie → Want → Need 完整弧线 + 声线卡 ≥5 维）、L3 重要配角（简版）、L2 功能性配角（极简）、L1 龙套（跳过）。反派必须单独做动机与镜像关系。层级可随剧情升级，升级时补全对应字段。L4/L3 完成后回访 02 做大纲精化，再进 04；写作中或审稿后回访，只补当前章涉及的角色。

### 04 世界构建 → `world.md`

从故事需求倒推，不做百科式铺陈。六步：倒推需求 → 规则体系 → 历史锚点 → 关键数值 → 禁忌与边界 → 写入。凡涉及数值、归属、外观，都要写成**可被 06 逐条比对**的明确表述。

### 05 初稿写作 → `content/chXX-draft.md`

写前七项检查（缺一不写）：未定稿章节检查 → 大纲定位 → 角色台账 → 进度文档 → 设定预读 → 外部系统 → 章首格式。区分两种情况：**情况 A 从零写**、**情况 B 已有初稿待修订**。正文前先输出「起草声明」，标明本章依据的大纲条目、涉及角色、需回收的伏笔。

### 06 修订审稿 → 修订 `chXX-draft.md`

四轮，逐轮过关，**不过不交付**：

1. **结构审查**——剧情逻辑、目标一致性、情绪与关系、身体与状态、场景转场、章末承接
2. **事实审查**——数值/归属/描述/时间线/角色状态，逐条比对 `world.md` 与 `tracking/`
3. **阅读体验审查**——节奏、信息投放、重复与冗余
4. **项目规则审查**——逐条比对 `rules.md` 的句式红线、标点规范

### 07 定稿输出 → `content/chXX.md`

前置：06 四轮全过。动作：平台格式适配（仅执行 `rules.md` 明确列出的项）→ 去掉 `-draft` 后缀转正。已是 `chXX.md` 的章节提示用户"已定稿"并退出，不重复处理。

### 08 追踪管理 → `tracking/*`

前置：章节已定稿。动作：更新 `progress.md`（章节摘要、时间线、伏笔状态、开放线索）与相关角色卡（能力、关系、状态变化）。新增设定同步回 `world.md`。

---

## 六、参考资产

### 阶段手册 `reference/phases/`

八个阶段各一份，统一结构：功能简介 → 触发条件 → 前置条件 → 流程 → 输出物 → 完成标准 → 常见错误 → 参考。**进入某阶段就加载对应手册**，不凭记忆执行。

### 专项模块 `reference/modules/`

局部硬伤专项，每个模块 6 件套（`README` / `tutorial` / `runtime` / `good_examples` / `bad_examples` / `source_index`）：

| 模块 | 解决什么 |
|---|---|
| `concept_planning` | 点子能否写成网文、卖点不亮 |
| `volume_outline` | 卷结构、章节排布 |
| `opening` | 开篇抓不住人 |
| `transition` | 场景/时间转场断裂 |
| `dialogue` | 对话像说明书、角色分不出 |
| `plot_logic` | 因果跳跃、反转无铺垫 |
| `character_consistency` | 人物 OOC、性格突变 |
| `chapter_ending` | 章末无钩子、承接断裂 |
| `anti_ai_voice` | AI 腔、句式模板化 |
| `consistency_review` | 二次以上返修、查漏补缺 |

调用原则：先判断是不是专项问题 → 读该模块 `README` → 按其入口顺序进 `tutorial`/`runtime` → 在例库匹配 2-4 正例、1-2 反例 → **只借结构，不借句面**。

### 参考文档 `reference/*.md`

按需加载，不常驻上下文：

| 文档 | 行数 | 何时加载 |
|---|---|---|
| `writing-techniques.md` | 743 | 进入 05 写作前一次性加载 |
| `genre-guides.md` | 280 | 01/02 确定类型时，读对应类型章节 |
| `image-prompts.md` | 461 | 生成角色图/场景图/封面时，读对应小节 |
| `platform-tactics.md` | 147 | 07 定稿适配，读目标平台章节 |
| `webnovel_corpus_guide.md` | 261 | 需要检索语料、做结构模仿时 |

### 语料 `data/` 与 `analysis/`

166 篇网文原文、664 条摘录、文风 profile 与 `imitation_index.md`（按「摘录类型 → 主题标签」索引）。检索与模仿的正确用法见 `webnovel_corpus_guide.md`。

---

## 七、穿插操作

**配图**：主要角色定稿后出角色图，重要场景首现后出场景图，完本后出封面。按 `image-prompts.md` 生成 prompt，存 `images/`，命名 `{角色名}.png` / `scene-{编号}.png` / `cover.png`。

**导出**：本 Skill 不再提供导出脚本。单章平台适配由 07 完成；全本导出交给 Studio 侧实现或用户手动合并。

---

## 八、重要约束

1. **一切落盘**：brief、大纲、角色卡、章节、台账都必须写入文件，绝不只存于对话。
2. **阶段不可跳**：01→02→03/04→05→06→07→08，前一阶段未产出、未确认，不进下一阶段。
3. **未定稿不开新章**：`content/` 存在 `-draft.md` 时，先提示用户定稿，再写新章。
4. **定稿靠后缀区分**：只有 07 才把 `chXX-draft.md` 改为 `chXX.md`，其他阶段不擅自改名。
5. **不静默覆盖定稿**：已定稿章节需用户明确要求才修改，修改前说明影响范围。
6. **权威优先于记忆**：任何一致性判断以 `brief/world/outline/rules/tracking` 为准。
7. **用户确认节点**：brief 定稿、outline 骨架、角色卡主体、每章定稿，四处必须用户明确确认。
8. **不引用不存在的工具**：本 Skill 无脚本可调用，初始化、统计、导出均按上文手工流程执行。
