from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.errors import APIError
from app.api.prompt_compilations import get_db
from app.db.models import ReferenceSource
from app.grounding import register_local, register_url_metadata, add_evidence, review_evidence, grounding_view, save_review
from app.visual_bibles import VisualBibleService, bible_response

router=APIRouter(tags=["grounding"])

def safe_source(s):
    return {"id":s.id,"title":s.title,"organization":s.organization,"source_type":s.source_type,"canonical_url":s.canonical_url,"page_or_section":s.page_or_section,"sha256":s.sha256,"mime_type":s.mime_type,"license":s.license,"usage_permission":s.usage_permission,"attribution":s.attribution,"review_status":s.review_status}

@router.post("/grounding/sources/register-local")
def register_source(payload: dict, db: Session=Depends(get_db)):
    try: return safe_source(register_local(db,payload))
    except ValueError as exc: raise APIError("INVALID_SOURCE",str(exc),422) from exc

@router.get("/grounding/sources/{source_id}")
def get_source(source_id: str, db: Session=Depends(get_db)):
    source=db.get(ReferenceSource,source_id)
    if not source: raise APIError("NOT_FOUND","Source not found",404)
    return safe_source(source)

@router.post("/grounding/sources/register-url-metadata")
def register_url(payload: dict, db: Session=Depends(get_db)):
    try: return safe_source(register_url_metadata(db,payload))
    except ValueError as exc: raise APIError("INVALID_SOURCE",str(exc),422) from exc

@router.post("/grounding/requirements/{requirement_id}/evidence")
def create_evidence(requirement_id: str,payload: dict,db: Session=Depends(get_db)):
    try:
        e=add_evidence(db,requirement_id,payload)
        return {"id":e.id,"grounding_requirement_id":e.grounding_requirement_id,"source_id":e.source_id,"review_status":e.review_status}
    except ValueError as exc: raise APIError("INVALID_EVIDENCE",str(exc),422) from exc

@router.post("/grounding/evidence/{evidence_id}/review")
def review(evidence_id: str,payload: dict,db: Session=Depends(get_db)):
    try:
        e=review_evidence(db,evidence_id,payload)
        return {"id":e.id,"review_status":e.review_status,"reviewer_id":e.reviewer_id}
    except ValueError as exc: raise APIError("INVALID_REVIEW",str(exc),409) from exc

@router.get("/visual-bibles/{bible_id}/grounding")
def get_grounding(bible_id: str,db: Session=Depends(get_db)):
    try:return grounding_view(db,bible_id)
    except ValueError as exc: raise APIError("NOT_FOUND",str(exc),404) from exc

@router.post("/visual-bibles/{bible_id}/character-reviews")
def character_review(bible_id: str,payload: dict,db: Session=Depends(get_db)):
    try:return {"id":save_review(db,bible_id,"CHARACTER",payload.get("target_id",""),payload).id}
    except ValueError as exc: raise APIError("INVALID_REVIEW",str(exc),409) from exc

@router.post("/visual-bibles/{bible_id}/environment-reviews")
def environment_review(bible_id: str,payload: dict,db: Session=Depends(get_db)):
    try:return {"id":save_review(db,bible_id,"ENVIRONMENT",payload.get("target_id",""),payload).id}
    except ValueError as exc: raise APIError("INVALID_REVIEW",str(exc),409) from exc

@router.post("/visual-bibles/{bible_id}/cultural-review")
def cultural_review(bible_id: str,payload: dict,db: Session=Depends(get_db)):
    try:return {"id":save_review(db,bible_id,"CULTURAL",bible_id,payload).id}
    except ValueError as exc: raise APIError("INVALID_REVIEW",str(exc),409) from exc
