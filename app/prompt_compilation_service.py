from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CulturalProfile as CulturalProfileRecord, PromptCompilationRecord, PromptModelProvenance
from app.prompt_compiler import (PromptCompilationRequest, PromptPlanner,
    ProjectPlan, is_historical_content, normalized_request, request_digest, validate_compiled_plan)
from app.ollama_prompt_planner import PlannerError
from app.prompt_planner_provider import configured_prompt_planner


def validation_warnings(request: PromptCompilationRequest, plan: ProjectPlan) -> list[str]:
    warnings = []
    prompt = request.prompt.casefold()
    regional = any(term in prompt for term in ("đồng bằng bắc bộ", "đồng bằng sông hồng", "châu thổ sông hồng"))
    if "việt nam" in prompt and not regional:
        warnings.append("Prompt says Vietnam without a specific region; regional grounding is required.")
    if any(term in prompt for term in ("bắc bộ", "miền bắc", "tây bắc")) and not regional:
        warnings.append("Northern Vietnam is named without a sufficiently specific subregion; do not assume the Red River Delta.")
    historical = is_historical_content(request.prompt)
    if historical and not any(term in prompt for term in ("thế kỷ", "năm ", "thời lý", "thời trần", "thời lê", "thời nguyễn", "hùng vương")):
        warnings.append("Historical content lacks a specified period; do not infer period, clothing, or architecture.")
    if historical and not any(term in prompt for term in ("tại ", "ở ", "vùng ", "kinh đô", "thăng long", "hoa lư", "cổ loa", "huế", "điện biên")):
        warnings.append("Historical content lacks a specified location; do not infer a historical setting.")
    if regional and any(term in prompt for term in ("miền nam", "tây nguyên", "nhà sàn", "cung điện trung hoa", "kiến trúc nhật")):
        warnings.append("Prompt contains potentially conflicting regional or period cues.")
    if not any(scene.source_reference_ids for scene in plan.scenes):
        warnings.append("No grounding source references are attached; scenes cannot be marked GROUNDED.")
    return warnings


class PromptCompilationService:
    def __init__(self, db: Session, planner: PromptPlanner | None = None) -> None:
        self.db = db
        self.planner = planner or configured_prompt_planner()

    def compile(self, request: PromptCompilationRequest) -> PromptCompilationRecord:
        cultural_version = self._cultural_profile_version(request.requested_cultural_profile)
        identity = self.planner.identity() if hasattr(self.planner, "identity") else {"provider": "mock", "model": None,
            "resolved_digest": self.planner.version, "template_version": "mock-template-v1"}
        digest = request_digest(request, self.planner, cultural_version, identity=identity)
        existing = self.db.scalar(select(PromptCompilationRecord).where(PromptCompilationRecord.request_hash == digest))
        if existing:
            return existing
        compilation_id = str(uuid4())
        now = datetime.now(UTC)
        execution = {"repair_attempts": 0, "validation_errors": [], "resource_metrics": {}, "latency_ms": None}
        try:
            plan = self.planner.compile(request, compilation_id)
            errors = validate_compiled_plan(request, plan)
            if errors:
                raise PlannerError("COMPILATION_FAILED", "planner output failed deterministic validation", errors)
            warnings = validation_warnings(request, plan)
            execution = getattr(self.planner, "execution_metadata", execution)
            status = "SUCCEEDED"
            plan_json = plan.model_dump_json(ensure_ascii=False)
            schema_version = plan.schema_version
        except PlannerError as exc:
            execution = getattr(self.planner, "execution_metadata", execution)
            execution["validation_errors"] = exc.validation_errors[:40] or [{"loc": [], "type": exc.code, "msg": exc.safe_message}]
            execution["validation_stage"] = exc.validation_stage
            execution["failed_scene_orders"] = exc.failed_scene_orders
            execution["error_count"] = len(execution["validation_errors"])
            status = "COMPILATION_FAILED"
            plan_json = None
            schema_version = "1.0"
            warnings = ["Compilation failed; no plan was persisted."]
        record = PromptCompilationRecord(id=compilation_id, request_hash=digest, raw_prompt=request.prompt,
            normalized_request_json=json.dumps(normalized_request(request), ensure_ascii=False, sort_keys=True),
            planner_type=self.planner.name, planner_version=self.planner.version, schema_version=schema_version,
            cultural_profile_version=cultural_version, plan_json=plan_json,
            validation_warnings_json=json.dumps(warnings, ensure_ascii=False), governance_state="DRAFT",
            compilation_status=status, planner_provider=identity.get("provider", "mock"),
            planner_model=identity.get("model"), resolved_model_digest=identity.get("resolved_digest"),
            prompt_template_version=identity.get("template_version", "mock-template-v1"),
            repair_attempts=execution.get("repair_attempts", 0),
            validation_errors_json=json.dumps(execution.get("validation_errors", []), ensure_ascii=False),
            resource_metrics_json=json.dumps(execution.get("resource_metrics", {}), ensure_ascii=False),
            planner_seed=identity.get("seed"), planner_temperature=identity.get("temperature"),
            latency_ms=execution.get("latency_ms"),
            validation_result_json=json.dumps({"valid": status == "SUCCEEDED", "errors": execution.get("validation_errors", []), "warnings": warnings}, ensure_ascii=False),
            validation_stage=execution.get("validation_stage", "complete" if status == "SUCCEEDED" else "planner"),
            error_count=execution.get("error_count", len(execution.get("validation_errors", []))),
            failed_scene_orders_json=json.dumps(execution.get("failed_scene_orders", []), ensure_ascii=False),
            candidate_response_sha256=execution.get("candidate_response_sha256"),
            candidate_diagnostic_path=execution.get("candidate_diagnostic_path"),
            timeline_provenance_json=json.dumps(execution.get("timeline_provenance", {}), ensure_ascii=False),
            created_at=now, updated_at=now)
        try:
            self.db.add(record)
            self._persist_provenance(identity)
            self.db.commit(); self.db.refresh(record)
        except Exception:
            self.db.rollback()
            record = self.db.scalar(select(PromptCompilationRecord).where(PromptCompilationRecord.request_hash == digest))
            if record is None:
                raise
        return record

    def _persist_provenance(self, identity: dict) -> None:
        digest = identity.get("resolved_digest")
        if identity.get("provider") != "ollama" or not digest:
            return
        record = self.db.get(PromptModelProvenance, digest)
        installed_at = identity.get("installed_at") or datetime.now(UTC).isoformat()
        try:
            installed_at = datetime.fromisoformat(installed_at.replace("Z", "+00:00"))
        except (AttributeError, ValueError):
            installed_at = datetime.now(UTC)
        values = dict(provider="ollama", ollama_version=identity.get("ollama_version"), requested_tag=identity.get("model") or "unknown",
            quantization=identity.get("quantization"), size_bytes=identity.get("size_bytes"),
            architecture=identity.get("architecture"), parameter_size=identity.get("parameter_size"),
            license=identity.get("license", "Apache-2.0"), installed_at=installed_at,
            prompt_template_version=identity.get("template_version", "unknown"))
        if record is None:
            self.db.add(PromptModelProvenance(resolved_model_digest=digest, **values))
        else:
            for key, value in values.items():
                setattr(record, key, value)

    def _cultural_profile_version(self, requested: str | None) -> str:
        if not requested:
            return "none"
        profile = self.db.get(CulturalProfileRecord, requested)
        if profile is None:
            profile = self.db.scalar(select(CulturalProfileRecord).where(CulturalProfileRecord.name == requested).order_by(CulturalProfileRecord.version.desc()))
        if profile is not None:
            return str(profile.version)
        match = re.search(r"-v(\d+)$", requested)
        return match.group(1) if match else "unregistered"

    def get(self, compilation_id: str) -> PromptCompilationRecord | None:
        return self.db.get(PromptCompilationRecord, compilation_id)

    def validate(self, record: PromptCompilationRecord) -> dict:
        if record.compilation_status != "SUCCEEDED" or record.plan_json is None:
            return {"valid": False, "warnings": json.loads(record.validation_warnings_json),
                    "errors": json.loads(record.validation_errors_json), "governance_status": record.governance_state}
        plan = ProjectPlan.model_validate_json(record.plan_json)
        warnings = validation_warnings(PromptCompilationRequest.model_validate_json(record.normalized_request_json), plan)
        record.validation_warnings_json = json.dumps(warnings, ensure_ascii=False)
        record.updated_at = datetime.now(UTC)
        self.db.commit()
        return {"valid": True, "warnings": warnings, "governance_status": record.governance_state}

    def approve_storyboard(self, record: PromptCompilationRecord) -> PromptCompilationRecord:
        if record.compilation_status != "SUCCEEDED" or record.plan_json is None:
            raise ValueError("failed compilations cannot be approved")
        plan = json.loads(record.plan_json)
        plan["governance_status"] = "STORYBOARD_APPROVED"
        record.plan_json = json.dumps(plan, ensure_ascii=False)
        record.governance_state = "STORYBOARD_APPROVED"
        record.updated_at = datetime.now(UTC)
        self.db.commit(); self.db.refresh(record)
        return record

    def update_scene(self, record: PromptCompilationRecord, scene_number: int, changes: dict) -> PromptCompilationRecord:
        updated_plan_json = edit_scene(record.plan_json, scene_number, changes)
        plan = ProjectPlan.model_validate_json(updated_plan_json)
        request = PromptCompilationRequest.model_validate_json(record.normalized_request_json)
        record.plan_json = plan.model_dump_json(ensure_ascii=False)
        record.governance_state = "DRAFT"
        record.validation_warnings_json = json.dumps(validation_warnings(request, plan), ensure_ascii=False)
        record.updated_at = datetime.now(UTC)
        self.db.commit(); self.db.refresh(record)
        return record


def record_response(record: PromptCompilationRecord) -> dict:
    return {"id": record.id, "request_hash": record.request_hash,
        "planner_type": record.planner_type, "planner_version": record.planner_version,
        "schema_version": record.schema_version, "governance_state": record.governance_state,
        "planner_provider": record.planner_provider, "planner_model": record.planner_model,
        "resolved_model_digest": record.resolved_model_digest,
        "prompt_template_version": record.prompt_template_version,
        "compilation_status": record.compilation_status, "repair_attempts": record.repair_attempts,
        "planner_seed": record.planner_seed, "planner_temperature": record.planner_temperature,
        "latency_ms": record.latency_ms, "validation_result": json.loads(record.validation_result_json or "{}"),
        "validation_stage": record.validation_stage, "error_count": record.error_count,
        "failed_scene_orders": json.loads(record.failed_scene_orders_json or "[]"),
        "candidate_response_sha256": record.candidate_response_sha256,
        "timeline_provenance": json.loads(record.timeline_provenance_json or "{}"),
        "validation_errors": json.loads(record.validation_errors_json),
        "resource_metrics": json.loads(record.resource_metrics_json),
        "validation_warnings": json.loads(record.validation_warnings_json),
        "created_at": record.created_at, "updated_at": record.updated_at}


def edit_scene(plan_json: str, scene_number: int, changes: dict) -> str:
    """Apply a storyboard edit and invalidate approvals from the edited scene onward."""
    plan = json.loads(plan_json)
    scenes = plan["scenes"]
    if not 1 <= scene_number <= len(scenes):
        raise ValueError("scene_number not found")
    allowed = {"title", "duration_seconds", "narration_vi", "learning_purpose", "visual_action",
               "camera_shot", "camera_motion", "motion_description", "positive_prompt_draft",
               "negative_prompt_draft", "sound_effects", "music_mood", "transition_out",
               "environment_id", "character_ids", "source_reference_ids"}
    if not changes or set(changes) - allowed:
        raise ValueError("invalid scene fields")
    scenes[scene_number - 1].update(changes)
    for scene in scenes[scene_number - 1:]:
        scene["content_review_status"] = "PENDING"
        scene["cultural_review_status"] = "PENDING"
        scene["keyframe_status"] = "NOT_GENERATED"
        scene["locked"] = False
    plan["governance_status"] = "DRAFT"
    plan["release_eligible"] = False
    return json.dumps(plan, ensure_ascii=False)
