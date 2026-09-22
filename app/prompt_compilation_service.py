from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CulturalProfile as CulturalProfileRecord, PromptCompilationRecord
from app.prompt_compiler import (DeterministicMockPromptPlanner,
    PromptCompilationRequest, PromptPlanner, ProjectPlan, is_historical_content, normalized_request, request_digest)


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
        self.planner = planner or DeterministicMockPromptPlanner()

    def compile(self, request: PromptCompilationRequest) -> PromptCompilationRecord:
        cultural_version = self._cultural_profile_version(request.requested_cultural_profile)
        digest = request_digest(request, self.planner, cultural_version)
        existing = self.db.scalar(select(PromptCompilationRecord).where(PromptCompilationRecord.request_hash == digest))
        if existing:
            return existing
        compilation_id = str(uuid4())
        plan = self.planner.compile(request, compilation_id)
        warnings = validation_warnings(request, plan)
        now = datetime.now(UTC)
        record = PromptCompilationRecord(id=compilation_id, request_hash=digest, raw_prompt=request.prompt,
            normalized_request_json=json.dumps(normalized_request(request), ensure_ascii=False, sort_keys=True),
            planner_type=self.planner.name, planner_version=self.planner.version, schema_version=plan.schema_version,
            cultural_profile_version=cultural_version,
            plan_json=plan.model_dump_json(ensure_ascii=False), validation_warnings_json=json.dumps(warnings, ensure_ascii=False),
            governance_state="DRAFT", created_at=now, updated_at=now)
        try:
            self.db.add(record); self.db.commit(); self.db.refresh(record)
        except Exception:
            self.db.rollback()
            record = self.db.scalar(select(PromptCompilationRecord).where(PromptCompilationRecord.request_hash == digest))
            if record is None:
                raise
        return record

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
        plan = ProjectPlan.model_validate_json(record.plan_json)
        warnings = validation_warnings(PromptCompilationRequest.model_validate_json(record.normalized_request_json), plan)
        record.validation_warnings_json = json.dumps(warnings, ensure_ascii=False)
        record.updated_at = datetime.now(UTC)
        self.db.commit()
        return {"valid": True, "warnings": warnings, "governance_status": record.governance_state}

    def approve_storyboard(self, record: PromptCompilationRecord) -> PromptCompilationRecord:
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
