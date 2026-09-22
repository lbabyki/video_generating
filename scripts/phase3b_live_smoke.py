#!/usr/bin/env python3
"""Run exactly one local Qwen storyboard compilation through the FastAPI API."""
from __future__ import annotations

import json
import sys
import time
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.main import app
from app.core.config import settings
from app.db.models import PromptCompilationRecord
from app.db.session import SessionLocal
from app.ollama_prompt_planner import LocalResourceGuard, OllamaQwenPromptPlanner
from app.prompt_compiler import PromptCompilationRequest, ProjectPlan, request_digest

FAILED_V1_ID = "939d36fc-2756-4743-8ce1-76aeabdec6b9"
EXPECTED_DIGEST = "bdbd181c33f2ed1b31c972991882db3cf4d192569092138a7d29e973cd9debe8"


def main() -> int:
    if settings.prompt_planner_provider != "ollama":
        print("FAIL: PROMPT_PLANNER_PROVIDER must explicitly be ollama", file=sys.stderr)
        return 2
    request = PromptCompilationRequest.model_validate_json(Path("fixtures/phase_3a_golden_request.json").read_text())
    planner = OllamaQwenPromptPlanner()
    try:
        identity = planner.identity()
        if (settings.ollama_model != "qwen3:14b" or identity.get("resolved_digest", "").removeprefix("sha256:") != EXPECTED_DIGEST
                or identity.get("quantization") != "Q4_K_M" or identity.get("license") != "Apache-2.0"
                or identity.get("template_version") != "phase3b-v2" or settings.prompt_planner_temperature != 0
                or settings.prompt_planner_seed != 314159 or settings.ollama_keep_alive not in {"0", "0s"}):
            print("FAIL: model, digest, quantization, license, template, temperature, seed, or keep_alive does not match the approved live run", file=sys.stderr)
            return 2
        guard = planner.resource_guard
        snapshot = guard.preflight(planner.max_gpu_utilization, planner.max_gpu_memory_mib)
        digest = request_digest(request, planner, "1", identity=identity)
        with SessionLocal() as db:
            previous_failure = db.get(PromptCompilationRecord, FAILED_V1_ID)
            previous_snapshot = None if previous_failure is None else (
                previous_failure.compilation_status, previous_failure.plan_json, previous_failure.request_hash,
                previous_failure.prompt_template_version, previous_failure.repair_attempts,
                previous_failure.validation_errors_json, previous_failure.updated_at)
            existing = db.scalar(select(PromptCompilationRecord).where(PromptCompilationRecord.request_hash == digest))
            if existing:
                print("FAIL: this exact resolved-model request already exists; refusing a non-live retry", file=sys.stderr)
                return 3
        preflight = {"gpu_utilization_percent": snapshot.utilization_percent,
                     "vram_before_mib": snapshot.memory_used_mib, "vram_total_mib": snapshot.memory_total_mib}
    finally:
        planner.close()

    started = time.perf_counter()
    with TestClient(app) as client:
        response = client.post("/prompt-compilations", json=request.model_dump(mode="json"))
        elapsed_seconds = round(time.perf_counter() - started, 3)
        if response.status_code != 200:
            print(json.dumps({"status_code": response.status_code, "error": response.json()}, ensure_ascii=False), file=sys.stderr)
            return 4
        compilation = response.json()
        if compilation["compilation_status"] != "SUCCEEDED" or not compilation.get("plan"):
            print(json.dumps({"compilation_status": compilation["compilation_status"],
                              "validation_errors": compilation.get("validation_errors"),
                              "repair_attempts": compilation.get("repair_attempts"),
                              "latency_ms": compilation.get("latency_ms"),
                              "compilation_id": compilation.get("id"),
                              "resource_metrics": compilation.get("resource_metrics")}, ensure_ascii=False), file=sys.stderr)
            return 5
        plan = ProjectPlan.model_validate(compilation["plan"])
        if not 7 <= len(plan.scenes) <= 10:
            raise RuntimeError("golden output must contain 7–10 scenes")
        durations = [Decimal(str(scene.duration_seconds)) for scene in plan.scenes]
        if sum(durations, Decimal("0")) != Decimal("45"):
            raise RuntimeError("golden output scene durations must sum exactly to 45 seconds")
        if any(duration < Decimal("3") or duration > Decimal("8") for duration in durations):
            raise RuntimeError("golden output includes a scene outside 3–8 seconds")
        if plan.cultural_profile_id != request.requested_cultural_profile:
            raise RuntimeError("golden output cultural profile does not match Red River Delta request")
        if len(plan.environments) != 1 or not (plan.environments[0].region == "NORTHERN_VIETNAM" and plan.environments[0].subregion == "RED_RIVER_DELTA"):
            raise RuntimeError("golden output has no Red River Delta environment")
        if plan.environments[0].terrain.casefold() not in {"flat_alluvial_plain", "flat alluvial plain", "alluvial plain, flat"}:
            raise RuntimeError("golden output terrain is not flat")
        if any(scene.environment_id != plan.environments[0].environment_id for scene in plan.scenes):
            raise RuntimeError("golden output did not reuse a stable environment ID across scenes")
        required_forbidden = {"núi cao", "làng nhà sàn", "kiến trúc cung điện trung hoa", "kiến trúc cung điện nhật"}
        if not any(required_forbidden <= {item.casefold() for item in env.forbidden_elements} for env in plan.environments):
            raise RuntimeError("golden output omitted required forbidden visual patterns")
        if not plan.characters or not plan.environments or any(scene.source_reference_ids for scene in plan.scenes):
            raise RuntimeError("golden output character/environment/reference contract failed")
        if not any(sum(character.character_id in scene.character_ids for scene in plan.scenes) >= 2 for character in plan.characters):
            raise RuntimeError("golden output did not reuse a stable character ID across scenes")
        if plan.grounding_status not in {"PENDING", "NEEDS_REVIEW"} or plan.governance_status != "DRAFT" or plan.release_eligible:
            raise RuntimeError("golden output grounding/governance gate failed")
        if any(scene.keyframe_status != "NOT_GENERATED" or scene.locked for scene in plan.scenes):
            raise RuntimeError("golden output must not create keyframes or locks")
        validation_response = client.post(f"/prompt-compilations/{compilation['id']}/validate")
        validation = validation_response.json()
        if validation_response.status_code != 200 or not validation.get("valid"):
            raise RuntimeError("persisted plan failed API deterministic validation")
        with SessionLocal() as db:
            new_record = db.get(PromptCompilationRecord, compilation["id"])
            if new_record.id == FAILED_V1_ID:
                raise RuntimeError("new attempt reused the failed v1 compilation ID")
            after_failure = db.get(PromptCompilationRecord, FAILED_V1_ID)
            after_snapshot = None if after_failure is None else (
                after_failure.compilation_status, after_failure.plan_json, after_failure.request_hash,
                after_failure.prompt_template_version, after_failure.repair_attempts,
                after_failure.validation_errors_json, after_failure.updated_at)
            if previous_snapshot != after_snapshot:
                raise RuntimeError("previous failed v1 record changed during the new attempt")

    metrics = compilation.get("resource_metrics", {})
    summary = {
        "status": "PASS",
        "compilation_id": compilation["id"],
        "request_hash": compilation["request_hash"],
        "planner_provider": compilation["planner_provider"],
        "planner_model": compilation["planner_model"],
        "quantization": identity["quantization"], "license": identity["license"],
        "resolved_model_digest": compilation["resolved_model_digest"],
        "prompt_template_version": compilation["prompt_template_version"],
        "seed": compilation["planner_seed"], "temperature": compilation["planner_temperature"],
        "scene_count": len(plan.scenes),
        "scene_durations_seconds": [float(value) for value in durations],
        "duration_seconds": float(sum(durations, Decimal("0"))),
        "character_ids": [character.character_id for character in plan.characters],
        "environment_ids": [environment.environment_id for environment in plan.environments],
        "grounding_status": plan.grounding_status,
        "governance_status": plan.governance_status,
        "repair_attempts": compilation["repair_attempts"],
        "validation_warnings": compilation["validation_warnings"],
        "validation": validation,
        "elapsed_seconds": elapsed_seconds,
        "preflight": preflight,
        "resource_metrics": metrics,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
