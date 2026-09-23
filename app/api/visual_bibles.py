from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.api.prompt_compilations import get_db
from app.visual_bibles import VisualBibleService, bible_response
from app.db.models import VisualPromptPackage

router = APIRouter(prefix="/visual-bibles", tags=["visual-bibles"])

def _get(db: Session, bible_id: str):
    bible = VisualBibleService(db).get(bible_id)
    if bible is None: raise APIError("NOT_FOUND", "Visual bible not found", 404)
    return bible

@router.post("/from-compilation/{compilation_id}")
def materialize(compilation_id: str, db: Session = Depends(get_db)):
    try: return bible_response(VisualBibleService(db).materialize(compilation_id), db)
    except ValueError as exc: raise APIError("INVALID_COMPILATION", str(exc), 409) from exc

@router.get("/{bible_id}")
def get_bible(bible_id: str, db: Session = Depends(get_db)): return bible_response(_get(db, bible_id), db)

@router.post("/{bible_id}/submit-review")
def submit_review(bible_id: str, db: Session = Depends(get_db)):
    try: return bible_response(VisualBibleService(db).submit_review(_get(db, bible_id)), db)
    except ValueError as exc: raise APIError("INVALID_STATE", str(exc), 409) from exc

@router.post("/{bible_id}/approve")
def approve(bible_id: str, db: Session = Depends(get_db)):
    try: return bible_response(VisualBibleService(db).approve(_get(db, bible_id)), db)
    except ValueError as exc: raise APIError("GOVERNANCE_BLOCKED", str(exc), 409) from exc

@router.post("/{bible_id}/lock")
def lock(bible_id: str, db: Session = Depends(get_db)):
    try: return bible_response(VisualBibleService(db).lock(_get(db, bible_id)), db)
    except ValueError as exc: raise APIError("GOVERNANCE_BLOCKED", str(exc), 409) from exc

@router.get("/{bible_id}/scene-prompts")
def scene_prompts(bible_id: str, db: Session = Depends(get_db)):
    bible = _get(db, bible_id)
    return [{"scene_id": p.scene_id, "positive_prompt": p.positive_prompt, "negative_prompt": p.negative_prompt, "package_hash": p.package_hash, "governance_status": p.governance_status, "release_eligible": p.release_eligible, "keyframe_status": p.keyframe_status, "valid": p.valid} for p in db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id==bible.id))]

@router.post("/{bible_id}/invalidate")
def invalidate(bible_id: str, db: Session = Depends(get_db)):
    try: return bible_response(VisualBibleService(db).invalidate(_get(db, bible_id)), db)
    except ValueError as exc: raise APIError("IMMUTABLE", str(exc), 409) from exc
