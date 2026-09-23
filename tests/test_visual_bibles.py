import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
import pytest

from app.db.models import Base, PromptCompilationRecord, VisualPromptPackage, VisualBibleSet
from app.prompt_compiler import DeterministicMockPromptPlanner, PromptCompilationRequest
from app.visual_bibles import VisualBibleService

def make_db():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    event.listen(engine,"connect",lambda conn,_: conn.execute("PRAGMA foreign_keys=ON")); Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine)()

def seed(db):
    req=PromptCompilationRequest.model_validate_json(open("fixtures/phase_3a_golden_request.json",encoding="utf-8").read())
    plan=DeterministicMockPromptPlanner().compile(req,"golden")
    row=PromptCompilationRecord(id="golden",request_hash="g"*64,raw_prompt=req.prompt,normalized_request_json=req.model_dump_json(),planner_type="mock",planner_version="mock",schema_version="1.0",cultural_profile_version="1",plan_json=plan.model_dump_json(),validation_warnings_json="[]",governance_state="DRAFT",compilation_status="SUCCEEDED",planner_provider="mock",planner_model=None,resolved_model_digest=None,prompt_template_version="mock",repair_attempts=0,validation_errors_json="[]",resource_metrics_json="{}",validation_result_json="{}",failed_scene_orders_json="[]",timeline_provenance_json="{}")
    db.add(row);db.commit(); return row

def test_materialize_counts_is_idempotent_and_does_not_change_compilation():
    engine,db=make_db(); row=seed(db); before=row.plan_json
    bible=VisualBibleService(db).materialize(row.id); again=VisualBibleService(db).materialize(row.id)
    assert bible.id==again.id and bible.status=="DRAFT" and row.plan_json==before
    from app.db.models import CharacterBible,EnvironmentBible,SceneVisualBinding,VisualPromptPackage
    assert len(db.scalars(select(CharacterBible).where(CharacterBible.bible_set_id==bible.id)).all())==2
    assert len(db.scalars(select(EnvironmentBible).where(EnvironmentBible.bible_set_id==bible.id)).all())>=2
    assert len(db.scalars(select(SceneVisualBinding).where(SceneVisualBinding.bible_set_id==bible.id)).all())==8
    assert len(db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id==bible.id)).all())==8
    db.close();engine.dispose()

def test_prompt_packages_are_deterministic_and_draft():
    engine,db=make_db(); bible=VisualBibleService(db).materialize(seed(db).id)
    packages=db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id==bible.id)).all()
    assert all(p.governance_status=="DRAFT" and not p.release_eligible and p.keyframe_status=="NOT_GENERATED" for p in packages)
    hashes=[p.package_hash for p in packages]; db.close();engine.dispose()
    engine,db=make_db(); bible2=VisualBibleService(db).materialize(seed(db).id)
    assert hashes == [p.package_hash for p in db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id==bible2.id)).all()]

def test_pending_grounding_blocks_approve_and_invalidate_marks_packages():
    engine,db=make_db(); bible=VisualBibleService(db).materialize(seed(db).id)
    with pytest.raises(ValueError,match="grounding"):
        VisualBibleService(db).approve(bible)
    VisualBibleService(db).invalidate(bible)
    assert not any(p.valid for p in db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id==bible.id)))
    db.close();engine.dispose()

def test_failed_compilation_cannot_materialize():
    engine,db=make_db(); row=seed(db); row.compilation_status="COMPILATION_FAILED"; row.plan_json=None; db.commit()
    with pytest.raises(ValueError,match="SUCCEEDED"): VisualBibleService(db).materialize(row.id)
    db.close();engine.dispose()
