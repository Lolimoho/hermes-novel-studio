# hermes-novel-studio

全流程网文小说创作 Skill，为 Hermes Agent 设计。

从构思 → 大纲 → 人物 → 写作 → 图片生成 → 修订 → 导出，覆盖小说创作全生命周期。

## 结构

```
hermes-novel-studio/
├── SKILL.md                    # 主入口：工作流编排
├── reference/                  # 按需加载的参考文档
│   ├── writing-techniques.md   # 网文写作技法（743行）
│   ├── genre-guides.md         # 各类型写作指南（280行）
│   ├── image-prompts.md        # 图片生成 Prompt 模板库（461行）
│   └── platform-tactics.md     # 平台发布策略（147行）
├── scripts/                    # 确定性工具脚本
│   ├── init_project.py         # 项目初始化
│   ├── stats.py                # 字数/进度统计
│   ├── export.py               # 全本手稿导出
│   └── continuity.py           # 连续性检查
└── templates/                  # 模板文件
    ├── chapter.md              # 章节写作模板
    ├── character-sheet.md      # 人物卡模板
    └── project/                # 项目模板
        ├── meta.json
        ├── outline.md
        └── worldbuilding.md
```
