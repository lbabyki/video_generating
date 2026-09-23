import json
import stat
from dataclasses import replace

import httpx
import pytest
from pydantic import BaseModel, ValidationError, model_validator
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.ollama_prompt_planner as planner_module
from app.db.models import Base, PromptCompilationRecord
from app.ollama_prompt_planner import GPUStats, OllamaQwenPromptPlanner, PlannerError, safe_pydantic_issues
from app.planner_candidate import CandidateProjectPlanCompiler, CandidateSemanticError, PlannerCandidate, resolve_terrain
from app.prompt_compilation_service import PromptCompilationService, record_response
from app.prompt_compiler import DeterministicMockPromptPlanner, PromptCompilationRequest


def request():
    return PromptCompilationRequest.model_validate_json(open("fixtures/phase_3a_golden_request.json", encoding="utf-8").read())


def candidate(scene_count=8):
    scenes = []
    for order in range(1, scene_count + 1):
        scenes.append({
            "scene_order": order, "title": f"Cảnh {order}", "narrative_purpose": "Bảo vệ môi trường",
            "visual_description": "Học sinh cùng người dân chăm sóc dòng sông và ruộng lúa.",
            "narration_text": "Cùng giữ gìn thiên nhiên quanh ta.",
            "characters": ["Lan", "Minh" if order == scene_count else "Lan"],
            "environment": "Đồng bằng Bắc Bộ", "cultural_constraints": [], "negative_constraints": [],
            "suggested_duration_seconds": 5.5,
        })
    return PlannerCandidate.model_validate({
        "title": "Bảo vệ thiên nhiên", "learning_objective": "Học sinh nêu hành động bảo vệ thiên nhiên.",
        "grounding_status": "PENDING",
        "characters": [
            {"name": "Lan", "role": "STUDENT", "age_group": "PRIMARY_SCHOOL", "visual_description": "Học sinh tiểu học.", "clothing_description": "Đồng phục giản dị."},
            {"name": "Minh", "role": "STUDENT", "age_group": "PRIMARY_SCHOOL", "visual_description": "Học sinh tiểu học khác.", "clothing_description": "Đồng phục giản dị."},
        ],
        "environments": [{"name": "Đồng bằng Bắc Bộ", "country": "VIETNAM", "region": "NORTHERN_VIETNAM",
            "subregion": "RED_RIVER_DELTA", "historical_period": "CONTEMPORARY", "terrain": "FLAT_ALLUVIAL_PLAIN",
            "architecture_profile": "NORTHERN_VIETNAMESE_RURAL", "visual_description": "Đồng bằng phẳng, có sông và ruộng lúa.",
            "required_elements": ["dòng sông", "ruộng lúa"], "cultural_constraints": [], "negative_constraints": []}],
        "scenes": scenes,
    })


def test_candidate_resolves_stable_entity_and_scene_ids_and_draft_plan():
    req = request()
    source = candidate()
    compiler = CandidateProjectPlanCompiler()
    first, provenance = compiler.compile(req, source, "compilation-one", "stable-request-hash")
    second, _ = compiler.compile(req, source, "compilation-two", "stable-request-hash")
    assert first.scenes[0].character_ids[0] == first.scenes[1].character_ids[0]
    assert first.scenes[0].environment_id == first.scenes[-1].environment_id
    assert [char.character_id for char in first.characters] != [char.character_id for char in first.characters[::-1]]
    assert first.characters[0].character_id == second.characters[0].character_id
    assert first.environments[0].environment_id == second.environments[0].environment_id
    assert [scene.scene_id for scene in first.scenes] == [scene.scene_id for scene in second.scenes]
    assert first.governance_status == "DRAFT" and first.release_eligible is False
    assert provenance["allocator_version"] == "largest-remainder-v1"
    assert provenance["adjusted"] is True


def test_seven_compatible_scene_locations_share_one_regional_profile():
    source = candidate().model_dump(mode="python")
    locations = ["Ruộng lúa", "Bờ sông", "Đường làng", "Sân đình", "Sân trường", "Hàng tre", "Khu dân cư"]
    source["environments"] = []
    source["scenes"] = source["scenes"][:7]
    for location in locations:
        source["environments"].append({
            "name": location, "country": "VIETNAM", "region": "NORTHERN_VIETNAM", "subregion": "RED_RIVER_DELTA",
            "historical_period": "CONTEMPORARY", "terrain": "FLAT_ALLUVIAL_PLAIN", "architecture_profile": "NORTHERN_VIETNAMESE_RURAL",
            "visual_description": f"{location} trong vùng đồng bằng phẳng.", "required_elements": [], "cultural_constraints": [], "negative_constraints": [],
        })
    for scene, location in zip(source["scenes"], locations):
        scene["environment"] = location
    plan, provenance = CandidateProjectPlanCompiler().compile(request(), PlannerCandidate.model_validate(source), "id", "hash")
    assert len({scene.environment_id for scene in plan.scenes}) == 7
    assert len({location.scene_location_id for location in plan.scene_locations}) == 7
    assert {location.regional_environment_profile_id for location in plan.scene_locations} == {plan.regional_environment_profile.regional_environment_profile_id}
    assert sum(scene.duration_seconds for scene in plan.scenes) == 45
    assert all(3 <= scene.duration_seconds <= 8 for scene in plan.scenes)
    assert provenance["regional_context"]["inherited_from_request"] is True


@pytest.mark.parametrize("alias", ["Đồng bằng Bắc Bộ", "Đồng bằng sông Hồng", "Red River Delta"])
def test_equivalent_region_aliases_normalize_to_red_river_delta(alias):
    source = candidate().model_dump(mode="python")
    source["environments"][0]["region"] = alias
    source["environments"][0]["subregion"] = alias
    req = PromptCompilationRequest.model_validate({**request().model_dump(mode="python"), "prompt": f"Video về {alias} và bảo vệ thiên nhiên."})
    plan, provenance = CandidateProjectPlanCompiler().compile(req, PlannerCandidate.model_validate(source), "id", "hash")
    assert plan.regional_environment_profile.canonical_region_key == "red-river-delta"
    assert provenance["regional_context"]["canonical_region_key"] == "red-river-delta"


@pytest.mark.parametrize("conflict", ["núi cao", "làng nhà sàn", "kiến trúc cung điện Trung Hoa", "kiến trúc cung điện Nhật Bản"])
def test_explicit_environment_conflicts_are_rejected_without_partial_plan(conflict):
    source = candidate().model_dump(mode="python")
    source["environments"][0]["visual_description"] += f" Có {conflict}."
    with pytest.raises(CandidateSemanticError) as caught:
        CandidateProjectPlanCompiler().compile(request(), PlannerCandidate.model_validate(source), "id", "hash")
    assert caught.value.issues[0]["type"] in {"regional_context_conflict", "terrain_not_flat"}


def test_different_semantic_entities_do_not_merge():
    plan, _ = CandidateProjectPlanCompiler().compile(request(), candidate(), "id", "request-hash")
    assert plan.characters[0].character_id != plan.characters[1].character_id


def test_unknown_semantic_reference_fails_before_project_plan_construction():
    source = candidate().model_dump(mode="python")
    source["scenes"][2]["characters"] = ["Unknown student"]
    invalid = PlannerCandidate.model_validate(source)
    with pytest.raises(CandidateSemanticError) as caught:
        CandidateProjectPlanCompiler().compile(request(), invalid, "id", "hash")
    assert caught.value.issues[0]["type"] == "unknown_character_reference"
    assert caught.value.failed_scene_orders == [3]


def test_semantic_reference_error_gets_one_candidate_repair():
    req = request()
    invalid = candidate().model_dump(mode="json")
    invalid["scenes"][1]["environment"] = "Unknown place"
    valid = candidate().model_dump(mode="json")
    responses = [json.dumps(invalid, ensure_ascii=False), json.dumps(valid, ensure_ascii=False)]
    client = httpx.Client(base_url="http://127.0.0.1:11434", transport=httpx.MockTransport(_ollama_handler(responses)))
    planner = OllamaQwenPromptPlanner(client=client, resource_guard=_Guard())
    plan = planner.compile(req, "semantic-repair")
    assert plan.scenes and planner.execution_metadata["repair_attempts"] == 1
    assert planner.execution_metadata["validation_stage"] == "complete"
    assert planner.execution_metadata["error_count"] == 0
    planner.close()


def test_timeline_infeasibility_does_not_trigger_model_repair():
    req = PromptCompilationRequest.model_validate({**request().model_dump(mode="python"), "target_duration_seconds": 15})
    responses = [json.dumps(candidate().model_dump(mode="json"), ensure_ascii=False)]
    client = httpx.Client(base_url="http://127.0.0.1:11434", transport=httpx.MockTransport(_ollama_handler(responses)))
    planner = OllamaQwenPromptPlanner(client=client, resource_guard=_Guard())
    with pytest.raises(PlannerError) as caught:
        planner.compile(req, "infeasible-timeline")
    assert getattr(caught.value, "code", None) == "TIMELINE_ALLOCATION_FAILED"
    assert planner.execution_metadata["repair_attempts"] == 0
    assert planner.execution_metadata["validation_stage"] == "timeline_allocation"
    planner.close()


def test_pydantic_model_errors_preserve_loc_type_message_and_safe_context():
    with pytest.raises(ValidationError) as caught:
        PlannerCandidate.model_validate({})
    issues = safe_pydantic_issues(caught.value)
    assert issues
    assert all({"loc", "type", "msg"} <= set(issue) for issue in issues)
    root = next(issue for issue in issues if issue["loc"] == ["title"])
    assert root["type"] == "missing" and root["msg"]


def test_pydantic_root_error_keeps_root_location_type_and_full_message():
    class RootFailure(BaseModel):
        value: int
        @model_validator(mode="after")
        def fail(self):
            raise ValueError("precise root invariant failed")
    with pytest.raises(ValidationError) as caught:
        RootFailure.model_validate({"value": 3})
    issue = safe_pydantic_issues(caught.value)[0]
    assert issue["loc"] == []
    assert issue["type"] == "value_error"
    assert "precise root invariant failed" in issue["msg"]


class _Guard:
    def preflight(self, *_): return GPUStats(0, 400, 32000)
    def measure_peak(self, initial_memory_mib=0): return lambda: {"vram_peak_mib": initial_memory_mib + 900}
    def ollama_running_models(self): return []
    def gpu_stats(self): return GPUStats(0, 400, 32000)


def _ollama_handler(response_values):
    responses = list(response_values)
    def handler(req):
        if req.url.path == "/api/version": return httpx.Response(200, json={"version": "0.32.6"})
        if req.url.path == "/api/tags": return httpx.Response(200, json={"models": [{"name": "qwen3:14b", "digest": "a" * 64, "details": {"quantization_level": "Q4_K_M"}}]})
        if req.url.path == "/api/generate":
            body = json.loads(req.content)
            if not body.get("prompt"): return httpx.Response(200, json={"response": "", "thinking": "untrusted hidden thought"})
            value = responses.pop(0)
            return httpx.Response(200, json={"response": value, "thinking": "untrusted hidden thought"})
        return httpx.Response(404)
    return handler


def test_failed_candidate_is_not_persisted_and_private_diagnostic_is_not_public_api(tmp_path, monkeypatch):
    req = request()
    invalid = candidate().model_dump(mode="json")
    invalid["thinking"] = "secret model thought"
    invalid_json = json.dumps(invalid, ensure_ascii=False)
    monkeypatch.setattr(planner_module, "settings", replace(planner_module.settings,
        prompt_planner_store_diagnostics=True, prompt_planner_diagnostics_dir=tmp_path))
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    http = httpx.Client(base_url="http://127.0.0.1:11434", transport=httpx.MockTransport(_ollama_handler([invalid_json, invalid_json])))
    planner = OllamaQwenPromptPlanner(client=http, resource_guard=_Guard())
    record = PromptCompilationService(db, planner).compile(req)
    public = record_response(record)
    assert record.compilation_status == "COMPILATION_FAILED" and record.plan_json is None
    assert record.validation_stage == "candidate_schema" and record.error_count > 0
    assert record.candidate_response_sha256 and len(record.candidate_response_sha256) == 64
    assert record.candidate_diagnostic_path
    diagnostic = open(record.candidate_diagnostic_path, encoding="utf-8").read()
    assert "secret model thought" not in diagnostic and "thinking" not in diagnostic
    assert stat.S_IMODE(__import__("os").stat(record.candidate_diagnostic_path).st_mode) == 0o600
    assert "candidate_diagnostic_path" not in public and "secret model thought" not in json.dumps(public, default=str)
    assert record.timeline_provenance_json == "{}"
    planner.close(); db.close(); engine.dispose()


def test_failed_v1_and_v2_records_are_untouched_by_later_compilation():
    # The actual database rows are never loaded by this test; it proves service writes are insert-only for other request hashes.
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    sentinel = []
    for version, identifier, request_hash in [
        ("phase3b-v1", "failed-v1", "1" * 64), ("phase3b-v2", "failed-v2", "2" * 64),
    ]:
        row = PromptCompilationRecord(id=identifier, request_hash=request_hash, raw_prompt="sentinel", normalized_request_json="{}",
            planner_type="OllamaQwenPromptPlanner", planner_version="1", schema_version="1.0", cultural_profile_version="1",
            plan_json=None, validation_warnings_json="[]", governance_state="DRAFT", compilation_status="COMPILATION_FAILED",
            planner_provider="ollama", planner_model="qwen3:14b", resolved_model_digest="digest", prompt_template_version=version,
            repair_attempts=1, validation_errors_json='[{"loc":[],"type":"sentinel","msg":"untouched"}]', resource_metrics_json="{}")
        db.add(row); sentinel.append(row)
    db.commit()
    before = [(row.id, row.request_hash, row.prompt_template_version, row.validation_errors_json, row.updated_at) for row in sentinel]
    PromptCompilationService(db, DeterministicMockPromptPlanner()).compile(request())
    after = [(row.id, row.request_hash, row.prompt_template_version, row.validation_errors_json, row.updated_at) for row in sentinel]
    assert after == before
    db.close(); engine.dispose()


@pytest.mark.parametrize("raw", ["flat", "flatland", "flat plain", "delta", "river delta", "alluvial plain", "low-lying plain", "bằng phẳng", "đồng bằng", "đồng bằng phù sa", "vùng châu thổ"])
def test_terrain_compatible_values_resolve_to_flat_delta(raw):
    result = resolve_terrain(raw, "red-river-delta")
    assert result["terrain_classification"] == "COMPATIBLE"
    assert result["resolved_terrain"] == "flat_delta"


@pytest.mark.parametrize("raw", ["rice field", "ruộng lúa", "riverbank", "bờ sông", "community garden", "vườn cây cộng đồng"])
def test_terrain_location_land_use_is_inherited_and_marked_misclassified(raw):
    result = resolve_terrain(raw, "red-river-delta")
    assert result["terrain_classification"] == "LOCATION_OR_LAND_USE"
    assert result["terrain_inherited_from_region"] is True
    assert result["model_field_misclassified"] is True


def test_missing_terrain_is_inherited_from_explicit_region():
    result = resolve_terrain(None, "red-river-delta")
    assert result["terrain_classification"] == "MISSING"
    assert result["resolved_terrain"] == "flat_delta"


def test_ambiguous_non_conflicting_terrain_is_reviewed_and_inherited():
    result = resolve_terrain("địa hình ven nước", "red-river-delta")
    assert result["terrain_classification"] == "AMBIGUOUS"
    assert result["review_required"] is True
    assert result["resolved_terrain"] == "flat_delta"


@pytest.mark.parametrize("raw", ["high mountain", "mountain valley", "plateau/highland", "núi cao", "thung lũng núi", "cao nguyên", "Tây Bắc", "Tây Nguyên"])
def test_terrain_explicit_conflicts_are_rejected(raw):
    result = resolve_terrain(raw, "red-river-delta")
    assert result["terrain_classification"] == "CONFLICT"
    assert result["conflict_detected"] is True


def test_v4_terrain_regression_fixture_resolves_without_conflict():
    fixture = json.load(open("fixtures/phase3b_r3/terrain_resolution_regression.json", encoding="utf-8"))
    results = [resolve_terrain(item["terrain"], "red-river-delta") for item in fixture["environments"]]
    assert all(item["resolved_terrain"] == "flat_delta" for item in results)
    assert all(not item["conflict_detected"] for item in results)


def test_conflicting_environment_only_marks_referencing_scene_orders():
    source = candidate().model_dump(mode="python")
    source["environments"].append({**source["environments"][0], "name": "Mountain", "terrain": "high mountain"})
    source["scenes"][2]["environment"] = "Mountain"
    with pytest.raises(CandidateSemanticError) as caught:
        CandidateProjectPlanCompiler().compile(request(), PlannerCandidate.model_validate(source), "id", "hash")
    assert caught.value.failed_scene_orders == [3]
