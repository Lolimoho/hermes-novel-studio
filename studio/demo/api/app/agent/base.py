"""Agent 适配器契约。

第一版只有 MockAdapter；接 Hermes 时实现同一接口即可，
上层（routers）不感知具体实现。
"""

from __future__ import annotations

from typing import Protocol

from ..models import Chapter, ChapterPlan, Project


class AgentAdapter(Protocol):
    name: str
    model: str

    def generate_plans(
        self, project: Project, start_seq: int, count: int, words: int
    ) -> list[dict]:
        """返回 count 条章蓝图草案，字段与 chapter_plan 对齐。"""
        ...

    def generate_draft(
        self, project: Project, chapter: Chapter, plan: ChapterPlan | None, note: str
    ) -> str:
        """返回本章候选稿正文（Markdown）。"""
        ...

    def review(
        self, project: Project, chapter: Chapter, plan: ChapterPlan | None, content: str
    ) -> list[dict]:
        """返回审稿意见，字段与 review_finding 对齐。"""
        ...
