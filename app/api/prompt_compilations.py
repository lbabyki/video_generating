import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.db.session import SessionLocal
from app.prompt_compilation_service import PromptCompilationService, record_response
from app.prompt_compiler import PromptCompilationRequest, ProjectPlan

router = APIRouter(prefix="/prompt-compilations", tags=["prompt-compilations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("")
def create_compilation(request: PromptCompilationRequest, db: Session = Depends(get_db)) -> dict:
    try:
        record = PromptCompilationService(db).compile(request)
    except ValueError as exc:
        raise APIError("INVALID_PROMPT", str(exc), 422) from exc
    result = record_response(record)
    result["plan"] = json.loads(record.plan_json)
    return result


def _record(db: Session, compilation_id: str):
    record = PromptCompilationService(db).get(compilation_id)
    if record is None:
        raise APIError("NOT_FOUND", "Prompt compilation not found", 404)
    return record


@router.get("/{compilation_id}")
def get_compilation(compilation_id: str, db: Session = Depends(get_db)) -> dict:
    return record_response(_record(db, compilation_id))


@router.get("/{compilation_id}/plan")
def get_plan(compilation_id: str, db: Session = Depends(get_db)) -> dict:
    record = _record(db, compilation_id)
    return json.loads(record.plan_json)


@router.post("/{compilation_id}/validate")
def validate_compilation(compilation_id: str, db: Session = Depends(get_db)) -> dict:
    service = PromptCompilationService(db)
    return service.validate(_record(db, compilation_id))


@router.post("/{compilation_id}/approve-storyboard")
def approve_storyboard(compilation_id: str, db: Session = Depends(get_db)) -> dict:
    service = PromptCompilationService(db)
    return record_response(service.approve_storyboard(_record(db, compilation_id)))


@router.patch("/{compilation_id}/scenes/{scene_number}")
def update_scene(compilation_id: str, scene_number: int, changes: dict, db: Session = Depends(get_db)) -> dict:
    service = PromptCompilationService(db)
    try:
        record = service.update_scene(_record(db, compilation_id), scene_number, changes)
    except ValueError as exc:
        raise APIError("INVALID_SCENE", str(exc), 422) from exc
    return {"compilation": record_response(record), "plan": json.loads(record.plan_json)}
