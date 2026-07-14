#!/usr/bin/env python3
"""
小说项目连续性检查工具

用法:
    python continuity.py <项目目录> [--verbose]

功能:
    - 读取 characters/ 下所有人物卡文件
    - 读取 outline.md 提取各章剧情点
    - 扫描 chapters/ 章节正文，做结构化基础检查：
        * 章节序号连续性
        * 人物在章节中的出场情况
        * 大纲剧情点覆盖（按关键词模糊匹配）
    - 需要语义理解的部分标记为 [NEED_LLM]
    - 输出结构化连续性报告

注意:
    本脚本做「基础结构检查」而非语义分析。
    人物行为一致性、情节逻辑等深层检查需要 LLM（Hermes Agent）接管，
    报告中会明确标记 [NEED_LLM] 条目以供后续处理。

依赖:
    标准库 only
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════════

@dataclass
class CharacterCard:
    """人物卡"""
    filename: str
    raw_text: str
    name: str = ""
    aliases: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)  # 解析出的键值对


@dataclass
class OutlineEntry:
    """大纲条目"""
    chapter_num: int
    title: str = ""
    plot_points: list = field(default_factory=list)  # 剧情点列表（字符串）


@dataclass
class ChapterContent:
    """章节内容"""
    filename: str
    chapter_num: int
    text: str = ""


@dataclass
class ContinuityReport:
    """连续性报告"""
    project_name: str = ""
    issues: list = field(default_factory=list)     # 问题列表
    need_llm: list = field(default_factory=list)   # [NEED_LLM] 条目
    notes: list = field(default_factory=list)      # 备注/信息
    summary: dict = field(default_factory=dict)    # 汇总


# ═══════════════════════════════════════════════════════════════
# 文件解析
# ═══════════════════════════════════════════════════════════════

def extract_chapter_number(filename: str) -> int:
    """从文件名提取章节序号。"""
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


def load_characters(characters_dir: str) -> list:
    """加载人物卡目录下所有文件。

    支持 .md 和 .txt 格式。
    尝试从文本中提取角色名（第一行的 # 标题，或文件名）。
    """
    cards = []
    if not os.path.isdir(characters_dir):
        return cards

    for fname in sorted(os.listdir(characters_dir)):
        if not (fname.endswith(".md") or fname.endswith(".txt")):
            continue
        fpath = os.path.join(characters_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"警告：无法读取人物卡 {fname} — {e}", file=sys.stderr)
            continue

        card = CharacterCard(filename=fname, raw_text=text)

        # 尝试提取角色名
        lines = text.strip().split("\n")
        if lines:
            first = lines[0].strip()
            if first.startswith("# ") or first.startswith("#"):
                card.name = first.lstrip("#").strip()
        if not card.name:
            # 用文件名（去除扩展名）
            card.name = os.path.splitext(fname)[0]

        # 提取别名（可能以「又名」「别名」「代号」等标注）
        alias_patterns = [
            r'别名[：:]s*(.+?)(?:\n|$)',
            r'又名[：:]s*(.+?)(?:\n|$)',
            r'代号[：:]s*(.+?)(?:\n|$)',
            r'昵称[：:]s*(.+?)(?:\n|$)',
        ]
        for pat in alias_patterns:
            m = re.search(pat, text)
            if m:
                aliases_str = m.group(1).strip()
                card.aliases = [a.strip() for a in re.split(r'[,，、/]', aliases_str) if a.strip()]

        # 提取属性键值对（如「年龄: 25」「性格: 沉稳」等）
        attr_pattern = re.compile(r'^[-*]*\s*([^\n：:]{1,10})[：:]\s*(.+?)$', re.MULTILINE)
        for m in attr_pattern.finditer(text):
            key = m.group(1).strip()
            val = m.group(2).strip()
            card.attributes[key] = val

        cards.append(card)

    return cards


def load_outline(project_dir: str) -> list:
    """解析 outline.md 提取章节剧情点。

    Returns:
        OutlineEntry 列表，按章节序号排列
    """
    outline_path = os.path.join(project_dir, "outline.md")
    if not os.path.isfile(outline_path):
        return []

    try:
        with open(outline_path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"警告：无法读取 outline.md — {e}", file=sys.stderr)
        return []

    entries = []
    # 按 ## 分割章节
    sections = re.split(r'\n(?=## )', text)

    for section in sections:
        header_match = re.match(r'^##\s*(.+)$', section.strip(), re.MULTILINE)
        if not header_match:
            continue

        header = header_match.group(1).strip()
        cn = extract_chapter_number(header)

        # 提取剧情点（以 - 或 * 开头的列表项）
        plot_points = re.findall(r'^\s*[-*]\s*(.+?)$', section, re.MULTILINE)

        entries.append(OutlineEntry(
            chapter_num=cn,
            title=header,
            plot_points=plot_points,
        ))

    # 按章节号排序
    entries.sort(key=lambda e: e.chapter_num)
    return entries


def load_chapters(chapters_dir: str) -> list:
    """加载所有章节正文。"""
    chapters = []
    if not os.path.isdir(chapters_dir):
        return chapters

    for fname in sorted(os.listdir(chapters_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(chapters_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"警告：无法读取章节 {fname} — {e}", file=sys.stderr)
            continue

        cn = extract_chapter_number(fname)
        chapters.append(ChapterContent(filename=fname, chapter_num=cn, text=text))

    chapters.sort(key=lambda c: c.chapter_num)
    return chapters


# ═══════════════════════════════════════════════════════════════
# 检查逻辑
# ═══════════════════════════════════════════════════════════════

def search_name_in_text(name: str, text: str) -> int:
    """搜索名字在文本中的出现次数。"""
    if not name:
        return 0
    # 转义正则特殊字符
    escaped = re.escape(name)
    return len(re.findall(escaped, text))


def search_aliases_in_text(aliases: list, text: str) -> dict:
    """搜索各别名在文本中的出现次数。"""
    result = {}
    for alias in aliases:
        count = len(re.findall(re.escape(alias), text))
        if count > 0:
            result[alias] = count
    return result


def check_character_presence(cards: list, chapters: list, report: ContinuityReport):
    """检查各人物在各章节中的出场情况。"""
    if not cards:
        report.notes.append("📝 characters/ 目录为空，跳过人物出场检查。")
        return

    if not chapters:
        report.notes.append("📝 chapters/ 目录为空，跳过人物出场检查。")
        return

    # 构建人物-章节出场矩阵
    presence = {}
    for card in cards:
        per_chapter = {}
        total_mentions = 0
        for ch in chapters:
            count = search_name_in_text(card.name, ch.text)
            alias_counts = search_aliases_in_text(card.aliases, ch.text)
            total = count + sum(alias_counts.values())
            if total > 0:
                per_chapter[ch.chapter_num] = {
                    "name_count": count,
                    "alias_counts": alias_counts,
                    "total": total,
                }
            total_mentions += total

        presence[card.name] = {
            "card": card,
            "chapters": per_chapter,
            "total_mentions": total_mentions,
        }

    # 发现：未出现在任何章节的人物
    not_appearing = []
    for name, data in presence.items():
        if data["total_mentions"] == 0:
            not_appearing.append(name)

    if not_appearing:
        report.issues.append({
            "type": "character_missing",
            "severity": "warning",
            "message": f"以下人物在已写章节中完全未出现: {', '.join(not_appearing)}",
            "detail": "可能尚未引入，或人物卡已创建但未使用。",
        })

    # [NEED_LLM] 人物出场是否符合设定
    # 基础检查：如果人物卡标注了 "首次出场: 第X章"，检查是否匹配
    for name, data in presence.items():
        card = data["card"]
        first_appear_attr = card.attributes.get("首次出场", "") or card.attributes.get("初登场", "")
        if first_appear_attr:
            expected_cn = extract_chapter_number(first_appear_attr)
            if expected_cn > 0:
                appearing = sorted(data["chapters"].keys())
                if appearing and min(appearing) != expected_cn:
                    report.issues.append({
                        "type": "character_first_appearance",
                        "severity": "info",
                        "message": f"人物「{name}」: 设定首次出场第{expected_cn}章，实际首次出现在第{min(appearing)}章",
                    })

    report.summary["character_presence"] = presence
    report.summary["characters_not_appearing"] = not_appearing


def check_chapter_continuity(chapters: list, report: ContinuityReport):
    """检查章节序号连续性。"""
    if not chapters:
        report.notes.append("📝 暂无章节文件。")
        return

    numbers = [ch.chapter_num for ch in chapters]

    # 重复序号
    seen = {}
    for ch in chapters:
        seen.setdefault(ch.chapter_num, []).append(ch.filename)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    for cn, fnames in duplicates.items():
        report.issues.append({
            "type": "duplicate_chapter",
            "severity": "error",
            "message": f"章节序号 {cn} 重复: {', '.join(fnames)}",
            "detail": "多个文件映射到同一章节序号，可能导致合并/导出时覆盖。",
        })

    # 缺漏序号
    max_num = max(numbers)
    min_num = min(min(numbers), 1)
    missing = sorted(set(range(min_num, max_num + 1)) - set(numbers))
    if missing:
        report.issues.append({
            "type": "missing_chapters",
            "severity": "warning",
            "message": f"缺漏章节序号: {missing}",
            "detail": "大纲中有对应编号但正文文件缺失，或章节编号不连续。",
        })

    report.summary["chapter_numbers"] = sorted(numbers)
    report.summary["missing_numbers"] = missing
    report.summary["duplicates"] = duplicates


def check_outline_coverage(outline: list, chapters: list, report: ContinuityReport):
    """检查大纲剧情点覆盖情况。

    对每个大纲剧情点，在对应章节正文中做关键词匹配。
    无法匹配的标记为可能遗漏。
    语义匹配标记为 [NEED_LLM]。
    """
    if not outline:
        report.notes.append("📝 outline.md 为空或不存在，跳过大纲覆盖检查。")
        return

    if not chapters:
        report.issues.append({
            "type": "outline_no_chapters",
            "severity": "warning",
            "message": "大纲已编写但暂无章节正文文件。",
        })
        return

    # 构建编号→正文映射
    chapter_texts = {ch.chapter_num: ch.text for ch in chapters}

    for entry in outline:
        cn = entry.chapter_num
        if cn not in chapter_texts:
            report.issues.append({
                "type": "outline_chapter_missing",
                "severity": "warning",
                "message": f"大纲「{entry.title}」对应的正文文件（第{cn}章）不存在。",
            })
            continue

        body = chapter_texts[cn].lower()

        for pp in entry.plot_points:
            # 提取关键词（去除括号说明、标点，取前几个实义词）
            keywords_str = re.sub(r'[【】《》（）\(\)""''，。！？、：；\s]', ' ', pp)
            keywords = [kw for kw in keywords_str.split() if len(kw) >= 2]

            if not keywords:
                continue

            # 检查至少一个关键词出现在正文中
            found = any(kw.lower() in body for kw in keywords)

            if not found:
                report.issues.append({
                    "type": "plot_point_unmatched",
                    "severity": "info",
                    "message": f"第{cn}章 大纲剧情点「{pp}」→ 正文中未找到关键词匹配",
                    "detail": f"搜索关键词: {keywords}",
                })
            else:
                # [NEED_LLM] 即使关键词匹配了，也需要语义验证
                report.need_llm.append({
                    "type": "plot_point_semantic",
                    "chapter": cn,
                    "plot_point": pp,
                    "message": f"第{cn}章「{pp}」→ 关键词已匹配，需 LLM 确认正文是否真正覆盖该剧情点",
                })

    # [NEED_LLM] 整体大纲-章节对应
    covered = set(entry.chapter_num for entry in outline)
    written = set(chapter_texts.keys())
    extra_chapters = written - covered
    if extra_chapters:
        report.need_llm.append({
            "type": "extra_chapters",
            "chapters": sorted(extra_chapters),
            "message": f"正文有章节（{sorted(extra_chapters)}）不在大纲中，需 LLM 判断是否为额外内容或大纲需更新。",
        })


def check_character_consistency(cards: list, report: ContinuityReport):
    """[NEED_LLM] 人物设定内部一致性基础检查。"""
    if not cards:
        return

    # 基础检查：有无缺少关键属性的人物卡
    for card in cards:
        missing_keys = []
        expected_keys = ["年龄", "性别", "性格"]
        for key in expected_keys:
            if key not in card.attributes:
                missing_keys.append(key)

        if missing_keys:
            report.need_llm.append({
                "type": "character_incomplete",
                "character": card.name,
                "missing_fields": missing_keys,
                "message": f"人物「{card.name}」缺少字段: {', '.join(missing_keys)}，可能影响一致性检查。",
            })

        # [NEED_LLM] 人物关系一致性需 LLM
        if "关系" in card.attributes or "身份" in card.attributes:
            report.need_llm.append({
                "type": "character_relationship",
                "character": card.name,
                "message": f"人物「{card.name}」有关系/身份设定，需 LLM 验证跨章节行为一致性。",
            })

    # [NEED_LLM] 人物间关系交叉验证
    report.need_llm.append({
        "type": "cross_character_consistency",
        "characters": [c.name for c in cards],
        "message": f"共 {len(cards)} 个人物，需 LLM 交叉验证人物关系、动机、行为的一致性。",
    })


def check_worldbuilding_references(project_dir: str, chapters: list, report: ContinuityReport):
    """[NEED_LLM] 检查章节对世界观设定的引用。"""
    wb_path = os.path.join(project_dir, "worldbuilding.md")
    if not os.path.isfile(wb_path):
        report.notes.append("📝 worldbuilding.md 不存在，跳过世界观一致性检查。")
        return

    try:
        with open(wb_path, "r", encoding="utf-8") as f:
            wb_text = f.read()
    except OSError:
        report.notes.append("📝 无法读取 worldbuilding.md，跳过世界观一致性检查。")
        return

    # 提取世界观中的关键地名、组织名等（简单提取 ## 标题下的关键词）
    sections = re.findall(r'^##\s*(.+)$', wb_text, re.MULTILINE)
    report.need_llm.append({
        "type": "worldbuilding_consistency",
        "sections": sections,
        "message": "需 LLM 检查各章节中的地名、组织、设定是否与 worldbuilding.md 一致。",
    })

    # 基础检查：章节中是否出现了世界观里未定义的关键名词（很难准确，标记 LLM）
    report.summary["worldbuilding_sections"] = sections


# ═══════════════════════════════════════════════════════════════
# 报告生成
# ═══════════════════════════════════════════════════════════════

def format_report(report: ContinuityReport, verbose: bool = False) -> str:
    """格式化连续性报告为可读文本。"""
    lines = []
    w = 70

    lines.append("=" * w)
    lines.append(f"  连续性检查报告 — {report.project_name}")
    lines.append("=" * w)
    lines.append("")

    # ── 摘要 ──
    lines.append("📊 摘要")
    lines.append("-" * w)
    issues_count = len(report.issues)
    llm_count = len(report.need_llm)
    notes_count = len(report.notes)

    sev = defaultdict(int)
    for iss in report.issues:
        sev[iss.get("severity", "info")] += 1

    lines.append(f"  发现问题: {issues_count} (错误: {sev.get('error', 0)}, 警告: {sev.get('warning', 0)}, 提示: {sev.get('info', 0)})")
    lines.append(f"  需 LLM 检查: {llm_count} 项")
    lines.append(f"  备注: {notes_count} 条")
    lines.append("")

    # ── 问题列表 ──
    if report.issues:
        lines.append("🔍 发现的问题")
        lines.append("-" * w)
        for i, iss in enumerate(report.issues, 1):
            sev_label = {"error": "❌ 错误", "warning": "⚠️ 警告", "info": "ℹ️ 提示"}.get(
                iss.get("severity", "info"), "📌"
            )
            lines.append(f"  [{i}] {sev_label} {iss['message']}")
            if verbose and iss.get("detail"):
                lines.append(f"      详情: {iss['detail']}")
        lines.append("")

    # ── 备注 ──
    if report.notes:
        lines.append("📝 备注")
        lines.append("-" * w)
        for note in report.notes:
            lines.append(f"  {note}")
        lines.append("")

    # ── [NEED_LLM] ──
    if report.need_llm:
        lines.append("🤖 需 LLM 检查项（Hermes Agent 接管）")
        lines.append("-" * w)
        llm_types = defaultdict(list)
        for item in report.need_llm:
            llm_types[item["type"]].append(item)

        for ttype, items in llm_types.items():
            type_names = {
                "plot_point_semantic": "大纲剧情点语义验证",
                "extra_chapters": "大纲外额外章节",
                "character_incomplete": "人物卡字段不完整",
                "character_relationship": "人物关系一致性",
                "cross_character_consistency": "人物间交叉一致性",
                "worldbuilding_consistency": "世界观设定一致性",
                "chapter_style_consistency": "章节风格一致性",
            }
            display = type_names.get(ttype, ttype)
            lines.append(f"  [NEED_LLM] {display} ({len(items)} 项)")
            if verbose:
                for item in items[:5]:  # 最多显示5条
                    lines.append(f"           → {item['message']}")
                if len(items) > 5:
                    lines.append(f"           → ... 还有 {len(items) - 5} 项")
        lines.append("")

    # ── 篇章信息 ──
    if "chapter_numbers" in report.summary:
        lines.append("📖 篇章信息")
        lines.append("-" * w)
        cn = report.summary["chapter_numbers"]
        if cn:
            lines.append(f"  已写章节: {cn}")
            lines.append(f"  章节数量: {len(cn)}")
        if report.summary.get("missing_numbers"):
            lines.append(f"  缺漏序号: {report.summary['missing_numbers']}")
        if report.summary.get("duplicates"):
            lines.append(f"  重复序号: {list(report.summary['duplicates'].keys())}")
        lines.append("")

    if "character_presence" in report.summary:
        presence = report.summary["character_presence"]
        lines.append("👤 人物出场统计")
        lines.append("-" * w)
        for name, data in presence.items():
            appearing = sorted(data["chapters"].keys())
            if appearing:
                lines.append(f"  {name}: 出现在第{appearing}章 (共{data['total_mentions']}次)")
            else:
                lines.append(f"  {name}: 未出场")
        lines.append("")

    lines.append("=" * w)
    return "\n".join(lines)


def run_continuity_check(project_dir: str, verbose: bool = False) -> ContinuityReport:
    """执行完整的连续性检查。

    Args:
        project_dir: 小说项目根目录
        verbose: 是否输出详细信息

    Returns:
        ContinuityReport 对象
    """
    project_name = os.path.basename(project_dir)
    report = ContinuityReport(project_name=project_name)

    characters_dir = os.path.join(project_dir, "characters")
    chapters_dir = os.path.join(project_dir, "chapters")

    # 校验目录
    if not os.path.isdir(project_dir):
        print(f"错误：项目目录不存在: {project_dir}", file=sys.stderr)
        sys.exit(1)

    # 加载数据
    cards = load_characters(characters_dir)
    outline = load_outline(project_dir)
    chapters = load_chapters(chapters_dir)

    report.summary["character_count"] = len(cards)
    report.summary["outline_entries"] = len(outline)
    report.summary["chapter_count"] = len(chapters)

    if verbose:
        print(f"📂 已加载 {len(cards)} 个人物卡, {len(outline)} 条大纲, {len(chapters)} 个章节")

    # 逐一检查
    check_chapter_continuity(chapters, report)
    check_character_presence(cards, chapters, report)
    check_outline_coverage(outline, chapters, report)
    check_character_consistency(cards, report)
    check_worldbuilding_references(project_dir, chapters, report)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="小说项目连续性检查（结构化基础检查 + [NEED_LLM] 标记）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python continuity.py ./novels/星辰陨落
    python continuity.py ./novels/星辰陨落 --verbose

说明:
    本脚本执行结构化基础检查（章节连续性、人物出场、剧情点关键词匹配）。
    需要语义理解的部分标记为 [NEED_LLM]，由 Hermes Agent 后续接管。
        """,
    )
    parser.add_argument("project_dir", help="小说项目根目录路径")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="输出详细信息",
    )
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)

    report = run_continuity_check(project_dir, verbose=args.verbose)
    print(format_report(report, verbose=args.verbose))


if __name__ == "__main__":
    main()
