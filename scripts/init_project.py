#!/usr/bin/env python3
"""
小说项目初始化工具

用法:
    python init_project.py <书名> [--output ./novels] [--force]

功能:
    - 创建完整的小说项目目录结构
    - 生成 meta.json 元数据文件
    - 生成初始 outline.md（大纲骨架）、worldbuilding.md（世界观）文件
    - 创建 characters/、chapters/、images/、export/ 子目录
    - 如果目录已存在，除非使用 --force，否则提示确认

目录结构:
    novels/<书名>/
        meta.json            # 项目元数据
        outline.md           # 大纲/剧情骨架
        worldbuilding.md     # 世界观设定
        characters/          # 人物卡目录
        chapters/            # 章节正文目录
        images/              # 插图/配图目录
        export/              # 导出输出目录
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone, timedelta


# ---- 模板内容 ----

META_TEMPLATE = {
    "title": "",
    "author": "",
    "genre": "",
    "style": "",
    "created_at": "",
    "updated_at": "",
    "status": "planning",
    "total_chapters": 0,
    "word_count": 0,
    "version": "1.0.0",
}

OUTLINE_SKELETON = """# {title} — 大纲

> 请在此编写小说大纲。每章一个二级标题，下面用列表列出关键剧情点。

---

## 第1章：开端
- 【剧情点1】
- 【剧情点2】
- 【剧情点3】

## 第2章：发展
- 【剧情点1】
- 【剧情点2】

## 第3章：高潮
- 【剧情点1】
- 【剧情点2】

## 第4章：结局
- 【剧情点1】
- 【剧情点2】

---

> 提示：可自由增删章节，Hermes Agent 会根据 outline.md 自动生成章节正文。
"""

WORLDBUILDING_SKELETON = """# 世界观设定 — {title}

## 时代背景
> 故事发生的年代、地区、社会环境。

-

## 地理环境
> 主要城市、地标、气候等。

-

## 势力/组织
> 各方势力、阵营、组织架构。

-

## 魔法/科技体系（如适用）
> 规则、等级、限制条件。

-

## 文化/习俗
> 节日、礼仪、禁忌等。

-

## 关键事件年表
> 故事前和故事中的重要历史事件。

-

---

> 提示：可自由扩展，Hermes Agent 参考此文件确保世界观一致性。
"""


# ---- 核心逻辑 ----

def build_dir_structure(base_dir: str, title: str) -> list:
    """构建需要创建的所有目录和文件路径列表。

    Args:
        base_dir: 项目根目录路径
        title: 书名

    Returns:
        (dirs, files) 两个列表，分别保存需要创建的目录和文件路径
    """
    dirs = [
        base_dir,
        os.path.join(base_dir, "characters"),
        os.path.join(base_dir, "chapters"),
        os.path.join(base_dir, "images"),
        os.path.join(base_dir, "export"),
    ]
    files = [
        (os.path.join(base_dir, "meta.json"), META_TEMPLATE, True),
        (os.path.join(base_dir, "outline.md"), OUTLINE_SKELETON, False),
        (os.path.join(base_dir, "worldbuilding.md"), WORLDBUILDING_SKELETON, False),
    ]
    return dirs, files


def create_project(title: str, output_dir: str, force: bool = False) -> str:
    """创建小说项目目录结构并写入模板文件。

    Args:
        title: 书名
        output_dir: 输出根目录（如 ./novels）
        force: 如果目录已存在，是否强制覆盖

    Returns:
        项目根目录路径

    Raises:
        SystemExit: 目录存在且用户拒绝覆盖时退出
    """
    # 安全处理书名中的特殊字符：替换路径分隔符和多余空格
    safe_title = title.strip().replace("/", "_").replace("\\", "_")
    if not safe_title:
        print("错误：书名不能为空。", file=sys.stderr)
        sys.exit(1)

    project_dir = os.path.join(output_dir, safe_title)
    project_dir = os.path.abspath(project_dir)

    # 检查目录是否已存在
    if os.path.exists(project_dir):
        if force:
            print(f"⚠ 目录已存在，--force 指定，将覆盖: {project_dir}")
            shutil.rmtree(project_dir)
        else:
            print(f"⚠ 目录已存在: {project_dir}")
            try:
                answer = input("是否覆盖？输入 y/yes 确认，其他任意键取消: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n已取消。", file=sys.stderr)
                sys.exit(1)
            if answer in ("y", "yes"):
                shutil.rmtree(project_dir)
                print("🗑 已删除旧目录，重新创建。")
            else:
                print("已取消。")
                sys.exit(0)

    # 创建目录
    dirs, file_specs = build_dir_structure(project_dir, safe_title)
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print(f"📁 目录结构已创建: {project_dir}")

    # 写入文件
    now_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    for filepath, content, is_json in file_specs:
        if is_json:
            content["title"] = safe_title
            content["created_at"] = now_str
            content["updated_at"] = now_str
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
                f.write("\n")
        else:
            filled = content.format(title=safe_title)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(filled)

    # 统计
    file_count = len(file_specs)
    dir_count = len(dirs)
    print(f"✅ 项目 '{safe_title}' 初始化完成！")
    print(f"   {dir_count} 个目录, {file_count} 个文件")
    print(f"   📄 meta.json — 项目元数据")
    print(f"   📄 outline.md — 大纲骨架")
    print(f"   📄 worldbuilding.md — 世界观设定")
    print(f"   📂 characters/ — 人物卡")
    print(f"   📂 chapters/ — 章节正文")
    print(f"   📂 images/ — 配图")
    print(f"   📂 export/ — 导出")
    return project_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="初始化小说项目目录结构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python init_project.py "星辰陨落"
    python init_project.py "星辰陨落" --output ./my_novels
    python init_project.py "星辰陨落" --force
        """,
    )
    parser.add_argument("title", help="书名（将作为目录名）")
    parser.add_argument(
        "--output",
        default="./novels",
        help="输出根目录，默认 ./novels",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="如果目录已存在，强制覆盖而不提问",
    )
    args = parser.parse_args()

    create_project(args.title, args.output, args.force)


if __name__ == "__main__":
    main()
