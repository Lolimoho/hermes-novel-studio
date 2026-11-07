from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Chapter, Character, Project, Revision, Volume
from ..schemas import (
    CharacterCreate,
    CharacterOut,
    CharacterUpdate,
    ProjectCreate,
    ProjectOut,
    ProjectSummary,
    ProjectUpdate,
    VolumeCreate,
    VolumeOut,
    VolumeUpdate,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectSummary])
def list_projects(db: Session = Depends(get_db)):
    projects = db.execute(select(Project).order_by(Project.updated_at.desc())).scalars().all()
    out: list[ProjectSummary] = []
    for p in projects:
        chapters = p.chapters
        word_count = 0
        for ch in chapters:
            if ch.current_revision_id:
                rev = db.get(Revision, ch.current_revision_id)
                if rev:
                    word_count += len(rev.content)
        out.append(
            ProjectSummary(
                **ProjectOut.model_validate(p).model_dump(),
                chapter_count=len(chapters),
                finalized_count=sum(1 for c in chapters if c.status == "finalized"),
                character_count=len(p.characters),
                word_count=word_count,
            )
        )
    return out


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "作品不存在")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "作品不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "作品不存在")
    db.delete(project)
    db.commit()


# ---------- 角色 ----------


@router.get("/{project_id}/characters", response_model=list[CharacterOut])
def list_characters(project_id: str, db: Session = Depends(get_db)):
    return (
        db.execute(
            select(Character)
            .where(Character.project_id == project_id)
            .order_by(Character.created_at)
        )
        .scalars()
        .all()
    )


@router.post("/{project_id}/characters", response_model=CharacterOut, status_code=201)
def create_character(project_id: str, payload: CharacterCreate, db: Session = Depends(get_db)):
    if not db.get(Project, project_id):
        raise HTTPException(404, "作品不存在")
    character = Character(project_id=project_id, **payload.model_dump())
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.patch("/characters/{character_id}", response_model=CharacterOut)
def update_character(character_id: str, payload: CharacterUpdate, db: Session = Depends(get_db)):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(404, "角色不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(character, key, value)
    db.commit()
    db.refresh(character)
    return character


@router.delete("/characters/{character_id}", status_code=204)
def delete_character(character_id: str, db: Session = Depends(get_db)):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(404, "角色不存在")
    db.delete(character)
    db.commit()


# ---------- 卷 ----------


@router.get("/{project_id}/volumes", response_model=list[VolumeOut])
def list_volumes(project_id: str, db: Session = Depends(get_db)):
    return (
        db.execute(select(Volume).where(Volume.project_id == project_id).order_by(Volume.seq))
        .scalars()
        .all()
    )


@router.post("/{project_id}/volumes", response_model=VolumeOut, status_code=201)
def create_volume(project_id: str, payload: VolumeCreate, db: Session = Depends(get_db)):
    if not db.get(Project, project_id):
        raise HTTPException(404, "作品不存在")
    max_seq = db.execute(
        select(func.max(Volume.seq)).where(Volume.project_id == project_id)
    ).scalar()
    volume = Volume(project_id=project_id, seq=(max_seq or 0) + 1, **payload.model_dump())
    db.add(volume)
    db.commit()
    db.refresh(volume)
    return volume


@router.patch("/volumes/{volume_id}", response_model=VolumeOut)
def update_volume(volume_id: str, payload: VolumeUpdate, db: Session = Depends(get_db)):
    volume = db.get(Volume, volume_id)
    if not volume:
        raise HTTPException(404, "卷不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(volume, key, value)
    db.commit()
    db.refresh(volume)
    return volume


@router.delete("/volumes/{volume_id}", status_code=204)
def delete_volume(volume_id: str, db: Session = Depends(get_db)):
    volume = db.get(Volume, volume_id)
    if not volume:
        raise HTTPException(404, "卷不存在")
    db.delete(volume)
    db.commit()
