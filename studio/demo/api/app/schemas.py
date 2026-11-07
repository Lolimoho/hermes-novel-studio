from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- project ----------


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    genre: str = ""
    audience: str = ""
    language: str = "zh"
    total_chapters: int = 30
    words_per_chapter: int = 3000
    premise: str = ""
    world_text: str = ""


class ProjectUpdate(BaseModel):
    title: str | None = None
    genre: str | None = None
    audience: str | None = None
    language: str | None = None
    total_chapters: int | None = None
    words_per_chapter: int | None = None
    premise: str | None = None
    world_text: str | None = None


class ProjectOut(ORMModel):
    id: str
    title: str
    genre: str
    audience: str
    language: str
    total_chapters: int
    words_per_chapter: int
    premise: str
    world_text: str
    created_at: datetime
    updated_at: datetime


class ProjectSummary(ProjectOut):
    chapter_count: int = 0
    finalized_count: int = 0
    character_count: int = 0
    word_count: int = 0


# ---------- character ----------


class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    level: str = "L2"
    function: str = ""
    desire: str = ""
    flaw: str = ""
    arc_note: str = ""
    status_note: str = ""


class CharacterUpdate(BaseModel):
    name: str | None = None
    level: str | None = None
    function: str | None = None
    desire: str | None = None
    flaw: str | None = None
    arc_note: str | None = None
    status_note: str | None = None


class CharacterOut(ORMModel):
    id: str
    project_id: str
    name: str
    level: str
    function: str
    desire: str
    flaw: str
    arc_note: str
    status_note: str


# ---------- volume ----------


class VolumeCreate(BaseModel):
    name: str = ""
    core_function: str = ""
    end_state: str = ""


class VolumeUpdate(BaseModel):
    name: str | None = None
    core_function: str | None = None
    end_state: str | None = None


class VolumeOut(ORMModel):
    id: str
    project_id: str
    seq: int
    name: str
    core_function: str
    end_state: str


# ---------- chapter ----------


class ChapterPlanOut(ORMModel):
    id: str
    title: str
    goal: str
    conflict: str
    hook: str
    cast: str
    words: int


class ChapterPlanUpdate(BaseModel):
    title: str | None = None
    goal: str | None = None
    conflict: str | None = None
    hook: str | None = None
    cast: str | None = None
    words: int | None = None


class ChapterOut(ORMModel):
    id: str
    project_id: str
    seq: int
    status: str
    current_revision_id: str | None
    plan: ChapterPlanOut | None


class RevisionOut(ORMModel):
    id: str
    chapter_id: str
    seq_no: int
    content: str
    source: str
    accepted_at: datetime | None
    approved_at: datetime | None
    created_at: datetime


class FindingOut(ORMModel):
    id: str
    chapter_id: str
    revision_id: str
    round: int
    severity: str
    category: str
    text: str
    status: str


class ChapterDetail(ChapterOut):
    revisions: list[RevisionOut] = []
    findings: list[FindingOut] = []


# ---------- 动作入参 ----------


class GeneratePlansIn(BaseModel):
    start_seq: int = 1
    count: int = 10
    words: int | None = None


class GenerateDraftIn(BaseModel):
    note: str = ""


class SaveDraftIn(BaseModel):
    content: str


class FindingUpdate(BaseModel):
    status: str


# ---------- run ----------


class RunOut(ORMModel):
    id: str
    project_id: str
    chapter_id: str | None
    kind: str
    status: str
    provider: str
    model: str
    started_at: datetime
    finished_at: datetime | None
    output_summary: str
    error: str
