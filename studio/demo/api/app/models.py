"""ORM 模型：与 docs/architecture/conceptual-data-model.md 一一对应。

主键统一 String(36) UUID 文本，时间统一 naive UTC，
以便 M1 迁移到 PostgreSQL 时只换方言不改模型。
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def uid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "project"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    genre: Mapped[str] = mapped_column(String(60), default="")
    audience: Mapped[str] = mapped_column(String(60), default="")
    language: Mapped[str] = mapped_column(String(10), default="zh")
    total_chapters: Mapped[int] = mapped_column(Integer, default=0)
    words_per_chapter: Mapped[int] = mapped_column(Integer, default=3000)
    premise: Mapped[str] = mapped_column(Text, default="")
    world_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    characters: Mapped[list[Character]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Character.created_at"
    )
    volumes: Mapped[list[Volume]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Volume.seq"
    )
    chapters: Mapped[list[Chapter]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Chapter.seq"
    )


class Character(Base):
    __tablename__ = "character"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    level: Mapped[str] = mapped_column(String(4), default="L2")
    function: Mapped[str] = mapped_column(String(200), default="")
    desire: Mapped[str] = mapped_column(Text, default="")
    flaw: Mapped[str] = mapped_column(Text, default="")
    arc_note: Mapped[str] = mapped_column(Text, default="")
    status_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    project: Mapped[Project] = relationship(back_populates="characters")


class Volume(Base):
    __tablename__ = "volume"
    __table_args__ = (UniqueConstraint("project_id", "seq", name="uq_volume_project_seq"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(120), default="")
    core_function: Mapped[str] = mapped_column(String(120), default="")
    end_state: Mapped[str] = mapped_column(Text, default="")

    project: Mapped[Project] = relationship(back_populates="volumes")


class Chapter(Base):
    __tablename__ = "chapter"
    __table_args__ = (UniqueConstraint("project_id", "seq", name="uq_chapter_project_seq"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    # not_started / draft / finalized
    status: Mapped[str] = mapped_column(String(16), default="not_started", nullable=False)
    # 故意不建外键：revision 反向引用 chapter，建 FK 会形成循环依赖。
    current_revision_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    project: Mapped[Project] = relationship(back_populates="chapters")
    plan: Mapped[ChapterPlan | None] = relationship(
        back_populates="chapter", uselist=False, cascade="all, delete-orphan"
    )
    revisions: Mapped[list[Revision]] = relationship(
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Revision.seq_no",
        foreign_keys="Revision.chapter_id",
    )
    findings: Mapped[list[ReviewFinding]] = relationship(
        back_populates="chapter", cascade="all, delete-orphan"
    )


class ChapterPlan(Base):
    __tablename__ = "chapter_plan"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    chapter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chapter.id", ondelete="CASCADE"), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), default="")
    goal: Mapped[str] = mapped_column(Text, default="")
    conflict: Mapped[str] = mapped_column(Text, default="")
    hook: Mapped[str] = mapped_column(String(200), default="")
    cast: Mapped[str] = mapped_column(Text, default="")
    words: Mapped[int] = mapped_column(Integer, default=3000)

    chapter: Mapped[Chapter] = relationship(back_populates="plan")


class Revision(Base):
    __tablename__ = "revision"
    __table_args__ = (
        UniqueConstraint("chapter_id", "seq_no", name="uq_revision_chapter_seq"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    chapter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chapter.id", ondelete="CASCADE"), index=True
    )
    seq_no: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    # ai / human / import
    source: Mapped[str] = mapped_column(String(10), default="human", nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    chapter: Mapped[Chapter] = relationship(
        back_populates="revisions", foreign_keys=[chapter_id]
    )
    findings: Mapped[list[ReviewFinding]] = relationship(back_populates="revision")


class ReviewFinding(Base):
    __tablename__ = "review_finding"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    chapter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chapter.id", ondelete="CASCADE"), index=True
    )
    revision_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("revision.id", ondelete="CASCADE"), index=True
    )
    round: Mapped[int] = mapped_column(Integer, default=1)
    # block / warn / hint
    severity: Mapped[str] = mapped_column(String(8), default="warn")
    # structure / fact / reading / rules
    category: Mapped[str] = mapped_column(String(20), default="structure")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # pending / accepted / rejected
    status: Mapped[str] = mapped_column(String(10), default="pending")

    chapter: Mapped[Chapter] = relationship(back_populates="findings")
    revision: Mapped[Revision] = relationship(back_populates="findings")


class Run(Base):
    __tablename__ = "run"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    chapter_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # plan_generation / draft_generation / review
    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    # running / succeeded / failed / cancelled
    status: Mapped[str] = mapped_column(String(10), default="running")
    provider: Mapped[str] = mapped_column(String(40), default="mock")
    model: Mapped[str] = mapped_column(String(80), default="mock-1")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    output_summary: Mapped[str] = mapped_column(Text, default="")
    error: Mapped[str] = mapped_column(Text, default="")
