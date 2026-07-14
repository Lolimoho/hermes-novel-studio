#!/usr/bin/env python3
"""
小说项目导出工具 — 全本手稿合并

用法:
    python export.py <项目目录> [--format md|txt] [--no-chapter-titles]

功能:
    - 按章节序号排序，合并 chapters/ 下所有 .md 文件
    - 生成目录页（Markdown 锚点链接）→ 仅 md 格式
    - 可选 --no-chapter-titles 去除每章标题，输出纯正文
    - 输出至 export/全书手稿.md 或 export/全书手稿.txt

依赖:
    标准库 only
"""

import argparse
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta


def extract_chapter_number(filename: str) -> int:
    """从文件名提取章节序号。

    支持格式: 第1章.md, chapter01.md, 001.md, 1.md, ch01.md
    """
    m = re.match(r'^(\d+)\.md$', filename)
    if m:
        return int(m.group(1))

    m = re.match(r'^第(\d+)章', filename)
    if m:
        return int(m.group(1))

    m = re.match(r'^(?:chapter|ch)[_-]?(\d+)', filename, re.IGNORECASE)
    if m:
        return int(m.group(1))

    m = re.search(r'(\d{2,})', filename)
    if m:
        return int(m.group(1))

    return 0


def get_chapter_title(text: str, filename: str) -> str:
    """从章节文本中提取标题。

    优先取第一个 # 标题，否则使用文件名作为标题。
    """
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") or stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    # 用文件名（去掉扩展名）
    return os.path.splitext(filename)[0]


def sanitize_anchor(title: str) -> str:
    """将标题转换为合法的 Markdown 锚点 ID。

    简化处理：移除特殊字符，中文保留（多数渲染器支持），空格换为连字符。
    """
    # 保留中文、英文、数字、空格、连字符
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
    cleaned = cleaned.strip().lower()
    cleaned = re.sub(r'\s+', '-', cleaned)
    return cleaned


def load_chapters(chapters_dir: str) -> list:
    """加载并排序章节文件。

    Returns:
        [(filename, chapter_num, content), ...] 按章节序号升序
    """
    entries = []
    for fname in os.listdir(chapters_dir):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(chapters_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"警告：无法读取 {fname} — {e}", file=sys.stderr)
            continue

        cn = extract_chapter_number(fname)
        entries.append((fname, cn, content))

    # 排序：序号 → 文件名
    entries.sort(key=lambda x: (x[1], x[0]))
    return entries


def build_toc(entries: list, include_titles: bool) -> str:
    """生成目录页（仅 Markdown）。

    Args:
        entries: [(fname, cn, content), ...]
        include_titles: 是否保留章节标题

    Returns:
        TOC 的 Markdown 字符串
    """
    lines = ["# 目录", ""]
    for i, (fname, cn, content) in enumerate(entries, 1):
        title = get_chapter_title(content, fname) if include_titles else f"第{cn}章" if cn else fname
        anchor = sanitize_anchor(title)
        lines.append(f"- [第{cn}章 {title}](#{anchor})" if cn else f"- [{title}](#{anchor})")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def strip_chapter_title(text: str) -> str:
    """去除章节开头的 # 标题行。"""
    lines = text.split("\n")
    result = []
    found_title = False
    for line in lines:
        stripped = line.strip()
        if not found_title and (stripped.startswith("# ") or stripped.startswith("#")):
            found_title = True
            continue
        result.append(line)
    return "\n".join(result)


def export_md(
    entries: list,
    project_name: str,
    generated_at: str,
    include_titles: bool,
    include_toc: bool,
) -> str:
    """生成 Markdown 格式全本手稿。

    Args:
        entries: 排序后的章节列表
        project_name: 书名
        generated_at: 生成时间字符串
        include_titles: 是否保留章节标题
        include_toc: 是否生成目录

    Returns:
        完整 Markdown 内容
    """
    lines = [
        f"# {project_name} — 全本手稿",
        "",
        f"> 生成时间：{generated_at}",
        f"> 总章节数：{len(entries)}",
        "",
        "---",
        "",
    ]

    if include_toc:
        lines.append(build_toc(entries, include_titles))

    for fname, cn, content in entries:
        title = get_chapter_title(content, fname)
        anchor = sanitize_anchor(title)

        if include_titles:
            lines.append(f"# 第{cn}章 {title}" if cn else f"# {title}")
            lines.append("")
            # 如果原文已有标题，去掉重复
            body = strip_chapter_title(content).strip()
        else:
            body = strip_chapter_title(content).strip()

        lines.append(body)
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def export_txt(
    entries: list,
    project_name: str,
    generated_at: str,
    include_titles: bool,
) -> str:
    """生成纯文本格式全本手稿。

    Args:
        entries: 排序后的章节列表
        project_name: 书名
        generated_at: 生成时间字符串
        include_titles: 是否保留章节标题

    Returns:
        完整纯文本内容
    """
    lines = [
        f"{project_name} — 全本手稿",
        f"生成时间：{generated_at}",
        f"总章节数：{len(entries)}",
        "",
        "=" * 60,
        "",
    ]

    chapter_label_num = 1
    for fname, cn, content in entries:
        title = get_chapter_title(content, fname)

        if include_titles:
            lines.append(f"第{cn}章 {title}" if cn else title)
            lines.append("")
            body = strip_chapter_title(content).strip()
        else:
            # 纯正文模式：在章节间用分隔线
            label = f"第{chapter_label_num}章 {title}" if include_titles else f"=== 第{chapter_label_num}章 ==="
            lines.append(label)
            lines.append("")
            body = strip_chapter_title(content).strip()

        # 纯正文模式不加标题时，正文直接拼接（不用编号）
        if not include_titles:
            lines.append(body)
            lines.append("")
            lines.append("")
        else:
            lines.append(body)
            lines.append("")
            lines.append("-" * 40)
            lines.append("")

        chapter_label_num += 1

    return "\n".join(lines)


def export_project(
    project_dir: str,
    fmt: str,
    include_titles: bool,
) -> str:
    """执行导出操作。

    Args:
        project_dir: 项目根目录
        fmt: 输出格式 ("md" 或 "txt")
        include_titles: 是否在输出中包含章节标题

    Returns:
        输出文件的路径
    """
    chapters_dir = os.path.join(project_dir, "chapters")
    if not os.path.isdir(chapters_dir):
        print(f"错误：chapters/ 目录不存在: {chapters_dir}", file=sys.stderr)
        sys.exit(1)

    export_dir = os.path.join(project_dir, "export")
    os.makedirs(export_dir, exist_ok=True)

    entries = load_chapters(chapters_dir)
    if not entries:
        print("错误：chapters/ 目录下没有 .md 章节文件。", file=sys.stderr)
        sys.exit(1)

    project_name = os.path.basename(project_dir)
    now_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

    if fmt == "md":
        output = export_md(entries, project_name, now_str, include_titles, include_toc=include_titles)
        ext = ".md"
    else:
        output = export_txt(entries, project_name, now_str, include_titles)
        ext = ".txt"

    filename = f"全书手稿{ext}"
    out_path = os.path.join(export_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)

    # 粗略字数十
    word_count = sum(
        sum(1 for c in entry[2] if '\u4e00' <= c <= '\u9fff')
        for entry in entries
    )

    print(f"✅ 导出完成: {out_path}")
    print(f"   格式: {fmt.upper()}")
    print(f"   章节数: {len(entries)}")
    print(f"   约字数: {word_count:,} 字")
    print(f"   时间: {now_str}")

    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="导出全本手稿（合并所有章节）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python export.py ./novels/星辰陨落
    python export.py ./novels/星辰陨落 --format txt
    python export.py ./novels/星辰陨落 --no-chapter-titles
        """,
    )
    parser.add_argument("project_dir", help="小说项目根目录路径")
    parser.add_argument(
        "--format", "-f",
        choices=["md", "txt"],
        default="md",
        help="输出格式: md（默认）或 txt",
    )
    parser.add_argument(
        "--no-chapter-titles",
        action="store_true",
        help="去除章节标题，只输出纯正文内容",
    )
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    if not os.path.isdir(project_dir):
        print(f"错误：项目目录不存在: {project_dir}", file=sys.stderr)
        sys.exit(1)

    include_titles = not args.no_chapter_titles
    export_project(project_dir, args.format, include_titles)


if __name__ == "__main__":
    main()
