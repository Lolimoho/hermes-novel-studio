#!/usr/bin/env python3
"""
小说项目字数与进度统计工具

用法:
    python stats.py <项目目录> [--json]

功能:
    - 扫描 chapters/ 下所有 .md 章节文件
    - 统计已完成章节数、总字数、每章字数、平均每章字数
    - 结合 meta.json 中的 total_chapters 计算进度百分比
    - 默认输出格式清晰的文本表格；--json 输出机器可读 JSON

依赖:
    标准库 only（无第三方依赖）
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ChapterStats:
    """单章统计"""
    filename: str
    chapter_num: int
    word_count: int = 0
    char_count: int = 0          # 含空格/标点的字符数
    pure_chinese: int = 0        # 纯中文字符数


@dataclass
class ProjectStats:
    """项目整体统计"""
    title: str = ""
    total_chapters: int = 0      # 计划总章节数
    completed_chapters: int = 0
    total_words: int = 0
    total_chars: int = 0
    total_chinese: int = 0
    avg_words: float = 0.0
    chapter_list: list = field(default_factory=list)
    progress: float = 0.0        # 百分比
    missing_numbers: list = field(default_factory=list)  # 缺的章节序号


def count_chinese(text: str) -> int:
    """统计纯中文字符数（不含标点、空格、英文）。"""
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')


def count_words(text: str) -> int:
    """统计总字数。

    中文按字计，英文/数字按词计（以空格分词）。
    中英混合时先分离再计数。
    """
    # 分离中文区域和非中文区域
    # 策略：对中文逐字计数，对非中文按空白分词的单词数计数
    total = 0
    buffer = []
    in_chinese = False

    for c in text:
        is_cn = '\u4e00' <= c <= '\u9fff'
        if is_cn:
            if not in_chinese and buffer:
                # 非中文缓冲区结束，计数
                total += len(''.join(buffer).split())
                buffer = []
            in_chinese = True
            total += 1
        else:
            if in_chinese and buffer:
                buffer = []
            in_chinese = False
            buffer.append(c)

    # 尾部非中文
    if not in_chinese and buffer:
        total += len(''.join(buffer).split())

    return total


def extract_chapter_number(filename: str) -> Optional[int]:
    """从文件名提取章节序号。

    支持格式: 第1章.md, chapter01.md, 001.md, 1.md, ch01.md
    """
    # 纯数字
    m = re.match(r'^(\d+)\.md$', filename)
    if m:
        return int(m.group(1))

    # 第N章
    m = re.match(r'^第(\d+)章', filename)
    if m:
        return int(m.group(1))

    # chapterN / chN
    m = re.match(r'^(?:chapter|ch)[_-]?(\d+)', filename, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # 从文件名中提取第一个出现的多位数字
    m = re.search(r'(\d{2,})', filename)
    if m:
        return int(m.group(1))

    return None


def load_meta(project_dir: str) -> dict:
    """加载 meta.json。"""
    meta_path = os.path.join(project_dir, "meta.json")
    if not os.path.isfile(meta_path):
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"警告：无法读取 meta.json — {e}", file=sys.stderr)
        return {}


def gather_stats(project_dir: str) -> ProjectStats:
    """收集项目统计信息。

    Args:
        project_dir: 项目根目录路径

    Returns:
        ProjectStats 对象
    """
    chapters_dir = os.path.join(project_dir, "chapters")
    if not os.path.isdir(chapters_dir):
        print(f"错误：chapters/ 目录不存在: {chapters_dir}", file=sys.stderr)
        sys.exit(1)

    meta = load_meta(project_dir)
    stats = ProjectStats(
        title=meta.get("title", os.path.basename(project_dir)),
        total_chapters=meta.get("total_chapters", 0),
    )

    # 扫描 .md 文件
    chapter_files = sorted([
        f for f in os.listdir(chapters_dir)
        if f.endswith(".md")
    ])

    existing_numbers = set()

    for fname in chapter_files:
        fpath = os.path.join(chapters_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"警告：无法读取 {fname} — {e}", file=sys.stderr)
            continue

        cn = extract_chapter_number(fname)
        if cn is None:
            cn = 0  # 无法识别序号
        else:
            existing_numbers.add(cn)

        ch = ChapterStats(
            filename=fname,
            chapter_num=cn,
            word_count=count_words(text),
            char_count=len(text),
            pure_chinese=count_chinese(text),
        )
        stats.chapter_list.append(ch)

    stats.chapter_list.sort(key=lambda c: (c.chapter_num, c.filename))
    stats.completed_chapters = len(stats.chapter_list)
    stats.total_words = sum(c.word_count for c in stats.chapter_list)
    stats.total_chars = sum(c.char_count for c in stats.chapter_list)
    stats.total_chinese = sum(c.pure_chinese for c in stats.chapter_list)

    if stats.completed_chapters > 0:
        stats.avg_words = round(stats.total_words / stats.completed_chapters, 1)
    else:
        stats.avg_words = 0.0

    # 进度
    if stats.total_chapters > 0:
        stats.progress = round(stats.completed_chapters / stats.total_chapters * 100, 1)
    elif stats.completed_chapters > 0:
        stats.progress = 100.0  # 无计划时，有章节就算100%
    else:
        stats.progress = 0.0

    # 检查缺漏
    if existing_numbers:
        max_num = max(existing_numbers)
        stats.missing_numbers = sorted(set(range(1, max_num + 1)) - existing_numbers)

    return stats


def format_text_table(stats: ProjectStats) -> str:
    """格式化为可读的文本表格。"""
    lines = []
    width = 60

    lines.append("=" * width)
    lines.append(f"  小说项目统计 — {stats.title}")
    lines.append("=" * width)
    lines.append(f"  计划章节数：{stats.total_chapters if stats.total_chapters else '(未设定)'}")
    lines.append(f"  已完成章节：{stats.completed_chapters}")
    lines.append(f"  总字数     ：{stats.total_words:,}")
    lines.append(f"  总字符数   ：{stats.total_chars:,}")
    lines.append(f"  纯中文     ：{stats.total_chinese:,}")
    lines.append(f"  平均每章   ：{stats.avg_words:,.1f} 字")
    lines.append(f"  完成进度   ：{stats.progress}%")
    lines.append("-" * width)

    if not stats.chapter_list:
        lines.append("  (暂无章节文件)")
    else:
        # 表头
        lines.append(f"  {'序号':>4}  {'文件名':<25} {'字数':>10} {'中文':>8}")
        lines.append("  " + "-" * (width - 2))

        for ch in stats.chapter_list:
            num_str = str(ch.chapter_num) if ch.chapter_num else "?"
            lines.append(
                f"  {num_str:>4}  {ch.filename:<25} {ch.word_count:>10,} {ch.pure_chinese:>8,}"
            )

    if stats.missing_numbers:
        lines.append("-" * width)
        lines.append(f"  ⚠ 缺漏章节序号: {', '.join(map(str, stats.missing_numbers))}")

    lines.append("=" * width)
    return "\n".join(lines)


def format_json(stats: ProjectStats) -> str:
    """格式化为 JSON。"""
    output = {
        "title": stats.title,
        "total_chapters_planned": stats.total_chapters,
        "completed_chapters": stats.completed_chapters,
        "total_words": stats.total_words,
        "total_chars": stats.total_chars,
        "total_chinese": stats.total_chinese,
        "avg_words_per_chapter": stats.avg_words,
        "progress_percent": stats.progress,
        "missing_chapter_numbers": stats.missing_numbers,
        "chapters": [
            {
                "filename": ch.filename,
                "chapter_num": ch.chapter_num,
                "word_count": ch.word_count,
                "char_count": ch.char_count,
                "pure_chinese": ch.pure_chinese,
            }
            for ch in stats.chapter_list
        ],
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="小说项目字数与进度统计",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python stats.py ./novels/星辰陨落
    python stats.py ./novels/星辰陨落 --json
        """,
    )
    parser.add_argument("project_dir", help="小说项目根目录路径")
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式（机器可读）",
    )
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    if not os.path.isdir(project_dir):
        print(f"错误：项目目录不存在: {project_dir}", file=sys.stderr)
        sys.exit(1)

    stats = gather_stats(project_dir)

    if args.json:
        print(format_json(stats))
    else:
        print(format_text_table(stats))


if __name__ == "__main__":
    main()
