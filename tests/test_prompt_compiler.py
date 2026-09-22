import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import app
from app.api.prompt_compilations import get_db
from app.db.models import Base, PromptCompilationRecord
from app.prompt_compilation_service import PromptCompilationService, edit_scene
from app.prompt_compiler import DeterministicMockPromptPlanner, PromptCompilationRequest, ProjectPlan, request_digest


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close(); engine.dispose()


def request(**updates):
    payload = {"prompt": "Video giáo dục bảo vệ thiên nhiên ở Đồng bằng Bắc Bộ, có sông, ruộng lúa, học sinh thu gom rác và trồng cây.", **updates}
    return PromptCompilationRequest.model_validate(payload)


def test_request_validation_rejects_empty_duration_enum_and_extra():
    for payload in ({"prompt": "  "}, {"prompt": "x", "target_duration_seconds": 2}, {"prompt": "x", "subject": "UNKNOWN"}, {"prompt": "x", "extra": 3}):
        with pytest.raises(ValueError): PromptCompilationRequest.model_validate(payload)


def test_prompt_length_and_wrong_types_rejected():
    with pytest.raises(ValueError): PromptCompilationRequest.model_validate({"prompt": "x" * 10001})
    with pytest.raises(ValueError): PromptCompilationRequest.model_validate({"prompt": "x", "target_duration_seconds": "45"})


def test_golden_auto_storyboard_contract():
    payload = json.loads(Path("fixtures/phase_3a_golden_request.json").read_text())
    req = PromptCompilationRequest.model_validate(payload)
    plan = DeterministicMockPromptPlanner().compile(req, "compilation-test")
    assert plan.title == "Bảo vệ thiên nhiên"
    assert len(plan.scenes) == 8
    assert sum(s.duration_seconds for s in plan.scenes) == 45
    assert plan.cultural_profile_id == "red-river-delta-v1"
    assert plan.environments[0].subregion == "RED_RIVER_DELTA"
    assert {"núi cao", "làng nhà sàn", "kiến trúc cung điện Trung Hoa", "kiến trúc cung điện Nhật"} <= set(plan.environments[0].forbidden_elements)
    assert plan.governance_status == "DRAFT" and not plan.release_eligible
    assert all(not s.locked and s.keyframe_status == "NOT_GENERATED" for s in plan.scenes)
    assert all(s.grounding_status != "GROUNDED" for s in plan.scenes)
    golden = json.loads(Path("fixtures/phase_3a_golden_output.json").read_text())
    reproducible = DeterministicMockPromptPlanner().compile(req, "00000000-0000-4000-8000-000000000003")
    assert golden["plan"] == reproducible.model_dump(mode="json")
    assert len(golden["plan"]["scenes"]) == 8


def test_explicit_scenes_keep_order_and_meaning():
    req = request(prompt="Cảnh 1: Mở cổng trường.\nCảnh 2: Học sinh tưới cây.\nCảnh 3: Cùng dọn sân.", mode="EXPLICIT_SCENES", target_duration_seconds=18)
    plan = DeterministicMockPromptPlanner().compile(req, "id")
    assert [s.narration_vi for s in plan.scenes] == ["Mở cổng trường.", "Học sinh tưới cây.", "Cùng dọn sân."]
    assert [s.scene_number for s in plan.scenes] == [1, 2, 3]


def test_scene_schema_enforces_duration_and_references():
    plan = DeterministicMockPromptPlanner().compile(request(), "id").model_dump()
    plan["scenes"][0]["duration_seconds"] = 9
    with pytest.raises(ValueError): ProjectPlan.model_validate(plan)
    plan = DeterministicMockPromptPlanner().compile(request(), "id").model_dump()
    plan["scenes"][0]["environment_id"] = "missing"
    with pytest.raises(ValueError): ProjectPlan.model_validate(plan)
    plan = DeterministicMockPromptPlanner().compile(request(), "id").model_dump()
    plan["scenes"][0]["character_ids"] = ["missing"]
    with pytest.raises(ValueError): ProjectPlan.model_validate(plan)
    plan = DeterministicMockPromptPlanner().compile(request(), "id").model_dump()
    plan["scenes"][0]["scene_number"] = 2
    with pytest.raises(ValueError): ProjectPlan.model_validate(plan)
    plan = DeterministicMockPromptPlanner().compile(request(), "id").model_dump()
    plan["scenes"][0]["duration_seconds"] += 0.2
    with pytest.raises(ValueError): ProjectPlan.model_validate(plan)
    plan = DeterministicMockPromptPlanner().compile(request(), "id").model_dump()
    plan["scenes"][0]["grounding_status"] = "GROUNDED"
    with pytest.raises(ValueError): ProjectPlan.model_validate(plan)


def test_vague_region_and_history_need_review():
    vague = request(prompt="Video về thiên nhiên Việt Nam cho học sinh.")
    plan = DeterministicMockPromptPlanner().compile(vague, "id")
    assert plan.grounding_status == "NEEDS_REVIEW"
    historical = request(prompt="Kể chuyện lịch sử về một triều đại Việt Nam.")
    plan = DeterministicMockPromptPlanner().compile(historical, "id")
    assert plan.grounding_status == "NEEDS_REVIEW"


def test_conflicting_regions_need_review():
    req = request(prompt="Đồng bằng Bắc Bộ thời lịch sử, có nhà sàn Tây Nguyên.")
    plan = DeterministicMockPromptPlanner().compile(req, "id")
    assert plan.grounding_status == "NEEDS_REVIEW"


def test_request_hash_and_retry_idempotent(db_session):
    req = request()
    planner = DeterministicMockPromptPlanner()
    assert request_digest(req, planner) == request_digest(request(prompt=req.prompt), planner)
    assert request_digest(req, planner) == request_digest(request(prompt="  " + req.prompt.replace(" ", "  ") + "  "), planner)
    first = PromptCompilationService(db_session, planner).compile(req)
    second = PromptCompilationService(db_session, planner).compile(req)
    assert first.id == second.id
    assert db_session.scalar(select(PromptCompilationRecord).where(PromptCompilationRecord.request_hash == first.request_hash))
    assert db_session.query(PromptCompilationRecord).count() == 1


def test_missing_source_warning_and_approval_invalidation(db_session):
    rec = PromptCompilationService(db_session).compile(request())
    validation = PromptCompilationService(db_session).validate(rec)
    assert any("No grounding source" in warning for warning in validation["warnings"])
    plan = json.loads(rec.plan_json)
    plan["governance_status"] = "STORYBOARD_APPROVED"
    for scene in plan["scenes"]: scene["content_review_status"] = scene["cultural_review_status"] = "APPROVED"
    changed = json.loads(edit_scene(json.dumps(plan), 2, {"title": "Đã chỉnh sửa"}))
    assert changed["governance_status"] == "DRAFT" and changed["release_eligible"] is False
    assert changed["scenes"][0]["content_review_status"] == "APPROVED"
    assert all(s["content_review_status"] == "PENDING" and s["cultural_review_status"] == "PENDING" for s in changed["scenes"][1:])


def test_api_create_get_validate_approve(db_session):
    def override_db(): yield db_session
    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app)
        response = client.post("/prompt-compilations", json=request().model_dump())
        assert response.status_code == 200
        assert response.json()["planner_provider"] == "mock"
        assert response.json()["compilation_status"] == "SUCCEEDED"
        assert response.json()["planner_model"] is None
        assert response.json()["resolved_model_digest"] == "mock-deterministic-v1"
        identifier = response.json()["id"]
        assert client.get(f"/prompt-compilations/{identifier}").status_code == 200
        assert client.get(f"/prompt-compilations/{identifier}/plan").json()["release_eligible"] is False
        assert client.post(f"/prompt-compilations/{identifier}/validate").json()["valid"]
        approved = client.post(f"/prompt-compilations/{identifier}/approve-storyboard").json()
        assert approved["governance_state"] == "STORYBOARD_APPROVED"
        final_plan = client.get(f"/prompt-compilations/{identifier}/plan").json()
        assert final_plan["governance_status"] == "STORYBOARD_APPROVED"
        assert final_plan["release_eligible"] is False
        assert all(s["content_review_status"] == "PENDING" and s["cultural_review_status"] == "PENDING" for s in final_plan["scenes"])
        record = db_session.get(PromptCompilationRecord, identifier)
        approved_plan = json.loads(record.plan_json)
        for scene in approved_plan["scenes"]:
            scene["content_review_status"] = scene["cultural_review_status"] = "APPROVED"
        record.plan_json = json.dumps(approved_plan)
        db_session.commit()
        edited = client.patch(f"/prompt-compilations/{identifier}/scenes/2", json={"title": "Bổ sung nội dung"}).json()
        assert edited["compilation"]["governance_state"] == "DRAFT"
        assert edited["plan"]["scenes"][0]["content_review_status"] == "APPROVED"
        assert all(s["content_review_status"] == "PENDING" and s["cultural_review_status"] == "PENDING" for s in edited["plan"]["scenes"][1:])
        assert client.post("/prompt-compilations", json={"prompt": "x", "unexpected": True}).status_code == 422
    finally:
        app.dependency_overrides.clear()
