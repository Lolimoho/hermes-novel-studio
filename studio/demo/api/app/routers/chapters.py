from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..agent.mock import MockAdapter
from ..db import get_db
from ..models import Chapter, ChapterPlan, Project, ReviewFinding, Revision, Run
from ..schemas import (
    ChapterDetail,
    ChapterOut,
    ChapterPlanUpdate,
    FindingOut,
    FindingUpdate,
    GenerateDraftIn,
    GeneratePlansIn,
    RevisionOut,
    SaveDraftIn,
)

router = APIRouter(tags=["chapters"])
adapter = MockAdapter()


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _new_run(db: Session, project_id: str, chapter_id: str | None, kind: str) -> Run:
    run = Run(
        project_id=project_id,
        chapter_id=chapter_id,
        kind=kind,
        status="running",
        provider=adapter.name,
        model=adapter.model,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def _finish_run(db: Session, run: Run, summary: str, status: str = "succeeded", error: str = ""):
    run.status = status
    run.output_summary = summary
    run.error = error
    run.finished_at = utcnow()
    db.commit()


def _next_rev_seq(db: Session, chapter_id: str) -> int:
    current = db.execute(
        select(func.max(Revision.seq_no)).where(Revision.chapter_id == chapter_id)
    ).scalar()
    return (current or 0) + 1


def _get_chapter(db: Session, chapter_id: str) -> Chapter:
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(404, "章节不存在")
    return chapter


# ---------- 蓝图 ----------


@router.get("/api/projects/{project_id}/chapters", response_model=list[ChapterOut])
def list_chapters(project_id: str, db: Session = Depends(get_db)):
    return (
        db.execute(select(Chapter).where(Chapter.project_id == project_id).order_by(Chapter.seq))
        .scalars()
        .all()
    )


@router.post("/api/projects/{project_id}/chapters/generate-plans", response_model=list[ChapterOut])
def generate_plans(project_id: str, payload: GeneratePlansIn, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "作品不存在")

    words = payload.words or project.words_per_chapter
    run = _new_run(db, project_id, None, "plan_generation")
    drafts = adapter.generate_plans(project, payload.start_seq, payload.count, words)

    created: list[Chapter] = []
    for index, item in enumerate(drafts):
        seq = payload.start_seq + index
        exists = db.execute(
            select(Chapter).where(Chapter.project_id == project_id, Chapter.seq == seq)
        ).scalar_one_or_none()
        if exists:
            continue
        chapter = Chapter(project_id=project_id, seq=seq)
        chapter.plan = ChapterPlan(**item)
        db.add(chapter)
        created.append(chapter)
    db.commit()

    _finish_run(db, run, f"生成 {len(created)} 章蓝图（第 {payload.start_seq} 章起）")
    for chapter in created:
        db.refresh(chapter)
    return created


@router.patch("/api/chapters/{chapter_id}/plan", response_model=ChapterOut)
def update_plan(chapter_id: str, payload: ChapterPlanUpdate, db: Session = Depends(get_db)):
    chapter = _get_chapter(db, chapter_id)
    if not chapter.plan:
        chapter.plan = ChapterPlan(chapter_id=chapter.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(chapter.plan, key, value)
    db.commit()
    db.refresh(chapter)
    return chapter


# ---------- 正文 ----------


@router.get("/api/chapters/{chapter_id}", response_model=ChapterDetail)
def get_chapter(chapter_id: str, db: Session = Depends(get_db)):
    chapter = _get_chapter(db, chapter_id)
    return ChapterDetail(
        **ChapterOut.model_validate(chapter).model_dump(),
        revisions=[RevisionOut.model_validate(r) for r in chapter.revisions],
        findings=[FindingOut.model_validate(f) for f in chapter.findings],
    )


@router.post("/api/chapters/{chapter_id}/generate", response_model=RevisionOut, status_code=201)
def generate_draft(
    chapter_id: str, payload: GenerateDraftIn, db: Session = Depends(get_db)
):
    chapter = _get_chapter(db, chapter_id)
    project = db.get(Project, chapter.project_id)
    run = _new_run(db, chapter.project_id, chapter.id, "draft_generation")

    content = adapter.generate_draft(project, chapter, chapter.plan, payload.note)
    revision = Revision(
        chapter_id=chapter.id,
        seq_no=_next_rev_seq(db, chapter.id),
        content=content,
        source="ai",
    )
    db.add(revision)
    db.commit()
    db.refresh(revision)

    _finish_run(db, run, f"第 {chapter.seq} 章候选稿 {len(content)} 字（待接受）")
    return revision


@router.post("/api/chapters/{chapter_id}/accept-candidate", response_model=ChapterOut)
def accept_candidate(chapter_id: str, db: Session = Depends(get_db)):
    chapter = _get_chapter(db, chapter_id)
    candidate = db.execute(
        select(Revision)
        .where(Revision.chapter_id == chapter.id, Revision.accepted_at.is_(None))
        .order_by(Revision.seq_no.desc())
    ).scalars().first()
    if not candidate:
        raise HTTPException(409, "没有可接受的候选稿")

    candidate.accepted_at = utcnow()
    chapter.status = "draft"
    chapter.current_revision_id = candidate.id
    db.commit()
    db.refresh(chapter)
    return chapter


@router.post("/api/chapters/{chapter_id}/save-draft", response_model=ChapterOut)
def save_draft(chapter_id: str, payload: SaveDraftIn, db: Session = Depends(get_db)):
    chapter = _get_chapter(db, chapter_id)
    revision = Revision(
        chapter_id=chapter.id,
        seq_no=_next_rev_seq(db, chapter.id),
        content=payload.content,
        source="human",
        accepted_at=utcnow(),
    )
    db.add(revision)
    db.commit()
    db.refresh(revision)

    chapter.status = "draft"
    chapter.current_revision_id = revision.id
    db.commit()
    db.refresh(chapter)
    return chapter


@router.post("/api/chapters/{chapter_id}/review", response_model=list[FindingOut])
def review(chapter_id: str, db: Session = Depends(get_db)):
    chapter = _get_chapter(db, chapter_id)
    if not chapter.current_revision_id:
        raise HTTPException(409, "本章还没有可审的稿子")
    revision = db.get(Revision, chapter.current_revision_id)
    if not revision:
        raise HTTPException(409, "当前版本不存在")

    project = db.get(Project, chapter.project_id)
    run = _new_run(db, chapter.project_id, chapter.id, "review")

    for old in db.execute(
        select(ReviewFinding).where(ReviewFinding.revision_id == revision.id)
    ).scalars():
        db.delete(old)

    items = adapter.review(project, chapter, chapter.plan, revision.content)
    findings = [ReviewFinding(chapter_id=chapter.id, revision_id=revision.id, **item) for item in items]
    for finding in findings:
        db.add(finding)
    db.commit()

    _finish_run(db, run, f"第 {chapter.seq} 章审稿：{len(findings)} 条意见")
    for finding in findings:
        db.refresh(finding)
    return findings


@router.patch("/api/findings/{finding_id}", response_model=FindingOut)
def update_finding(finding_id: str, payload: FindingUpdate, db: Session = Depends(get_db)):
    finding = db.get(ReviewFinding, finding_id)
    if not finding:
        raise HTTPException(404, "审稿意见不存在")
    if payload.status not in {"pending", "accepted", "rejected"}:
        raise HTTPException(400, "status 只能是 pending / accepted / rejected")
    finding.status = payload.status
    db.commit()
    db.refresh(finding)
    return finding


@router.post("/api/chapters/{chapter_id}/finalize", response_model=ChapterOut)
def finalize(chapter_id: str, db: Session = Depends(get_db)):
    chapter = _get_chapter(db, chapter_id)
    if not chapter.current_revision_id:
        raise HTTPException(409, "本章还没有稿子，无法定稿")

    blocking = db.execute(
        select(ReviewFinding).where(
            ReviewFinding.revision_id == chapter.current_revision_id,
            ReviewFinding.severity == "block",
            ReviewFinding.status == "pending",
        )
    ).scalars().all()
    if blocking:
        raise HTTPException(
            409, f"还有 {len(blocking)} 条阻断级意见未处理，不能定稿"
        )

    revision = db.get(Revision, chapter.current_revision_id)
    revision.approved_at = utcnow()
    chapter.status = "finalized"
    db.commit()
    db.refresh(chapter)
    return chapter


@router.post("/api/chapters/{chapter_id}/reopen", response_model=ChapterOut)
def reopen(chapter_id: str, db: Session = Depends(get_db)):
    chapter = _get_chapter(db, chapter_id)
    if chapter.status != "finalized":
        raise HTTPException(409, "只有已定稿的章节需要重新打开")
    chapter.status = "draft"
    db.commit()
    db.refresh(chapter)
    return chapter


@router.post("/api/chapters/{chapter_id}/revert/{revision_id}", response_model=ChapterOut)
def revert(chapter_id: str, revision_id: str, db: Session = Depends(get_db)):
    chapter = _get_chapter(db, chapter_id)
    target = db.get(Revision, revision_id)
    if not target or target.chapter_id != chapter.id:
        raise HTTPException(404, "目标版本不属于本章")

    revision = Revision(
        chapter_id=chapter.id,
        seq_no=_next_rev_seq(db, chapter.id),
        content=target.content,
        source="human",
        accepted_at=utcnow(),
    )
    db.add(revision)
    db.commit()
    db.refresh(revision)

    chapter.status = "draft"
    chapter.current_revision_id = revision.id
    db.commit()
    db.refresh(chapter)
    return chapter
