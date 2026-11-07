from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Run
from ..schemas import RunOut

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("", response_model=list[RunOut])
def list_runs(project_id: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    stmt = select(Run).order_by(Run.started_at.desc()).limit(limit)
    if project_id:
        stmt = (
            select(Run)
            .where(Run.project_id == project_id)
            .order_by(Run.started_at.desc())
            .limit(limit)
        )
    return db.execute(stmt).scalars().all()


@router.get("/{run_id}", response_model=RunOut)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(404, "运行记录不存在")
    return run
