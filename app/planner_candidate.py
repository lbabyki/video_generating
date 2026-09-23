"""Candidate schema and deterministic conversion to the release-ineligible plan."""
from __future__ import annotations

import re
import unicodedata
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field, ValidationError

from app.prompt_compiler import (
    CharacterReference,
    EnvironmentReference,
    ProjectPlan,
    PromptCompilationRequest,
    ScenePlan,
    StrictModel,
    is_historical_content,
)
from app.timeline_allocator import DeterministicTimelineAllocator, TimelineAllocationError


class PlannerCandidateCharacter(StrictModel):
    name: str = Field(min_length=1, max_length=160)
    role: str = Field(min_length=1, max_length=240)
    age_group: str = Field(min_length=1, max_length=120)
    visual_description: str = Field(min_length=1, max_length=1200)
    clothing_description: str = Field(min_length=1, max_length=800)
    continuity_constraints: list[str] = Field(default_factory=list, max_length=20)


class PlannerCandidateEnvironment(StrictModel):
    name: str = Field(min_length=1, max_length=160)
    country: str = Field(min_length=1, max_length=120)
    region: str = Field(min_length=1, max_length=120)
    subregion: str = Field(min_length=1, max_length=120)
    historical_period: str = Field(min_length=1, max_length=120)
    terrain: str = Field(min_length=1, max_length=160)
    architecture_profile: str = Field(min_length=1, max_length=200)
    visual_description: str = Field(min_length=1, max_length=1600)
    required_elements: list[str] = Field(default_factory=list, max_length=30)
    cultural_constraints: list[str] = Field(default_factory=list, max_length=30)
    negative_constraints: list[str] = Field(default_factory=list, max_length=40)


class PlannerCandidateScene(StrictModel):
    scene_order: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=240)
    narrative_purpose: str = Field(min_length=1, max_length=600)
    visual_description: str = Field(min_length=1, max_length=1600)
    narration_text: str = Field(min_length=1, max_length=1600)
    characters: list[str] = Field(min_length=1, max_length=20)
    environment: str = Field(min_length=1, max_length=160)
    cultural_constraints: list[str] = Field(default_factory=list, max_length=30)
    negative_constraints: list[str] = Field(default_factory=list, max_length=40)
    suggested_duration_seconds: float | None = Field(default=None, ge=0)
    duration_weight: float | None = Field(default=None, gt=0)


class PlannerCandidate(StrictModel):
    """Unapproved semantic content. Contains no final IDs, media, or source IDs."""
    title: str = Field(min_length=1, max_length=240)
    learning_objective: str = Field(min_length=1, max_length=800)
    grounding_status: Literal["PENDING", "NEEDS_REVIEW"] = "PENDING"
    characters: list[PlannerCandidateCharacter] = Field(min_length=1, max_length=30)
    environments: list[PlannerCandidateEnvironment] = Field(min_length=1, max_length=20)
    scenes: list[PlannerCandidateScene] = Field(min_length=7, max_length=10)


class CandidateSemanticError(ValueError):
    def __init__(self, issues: list[dict], failed_scene_orders: list[int] | None = None):
        super().__init__("planner candidate failed semantic validation")
        self.issues = issues
        self.failed_scene_orders = sorted(set(failed_scene_orders or []))


def safe_pydantic_issues(exc: ValidationError, limit: int = 40) -> list[dict]:
    issues = []
    for item in exc.errors()[:limit]:
        context = {}
        for key, value in (item.get("ctx") or {}).items():
            if value is None or isinstance(value, (str, int, float, bool)):
                context[str(key)] = value if not isinstance(value, str) else value[:240]
            elif isinstance(value, (list, tuple)):
                context[str(key)] = [str(part)[:120] for part in value[:10]]
            else:
                context[str(key)] = str(value)[:240]
        issues.append({
            "loc": list(item.get("loc", ())),
            "type": str(item.get("type", "invalid")),
            "msg": str(item.get("msg", "Invalid value"))[:500],
            **({"context": context} if context else {}),
        })
    return issues


def semantic_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"\s+", " ", normalized).strip()


def validate_candidate_semantics(candidate: PlannerCandidate, request: PromptCompilationRequest | None = None) -> tuple[list[dict], list[int]]:
    issues: list[dict] = []
    failed: set[int] = set()
    if not 7 <= len(candidate.scenes) <= 10:
        issues.append({"loc": ["scenes"], "type": "scene_count_out_of_range", "msg": "Candidate must contain 7–10 scenes."})
        failed.update(scene.scene_order for scene in candidate.scenes)
    actual_orders = [scene.scene_order for scene in candidate.scenes]
    if actual_orders != list(range(1, len(actual_orders) + 1)):
        issues.append({"loc": ["scenes"], "type": "scene_order_invalid", "msg": "scene_order values must be unique, continuous, and ordered."})
        failed.update(actual_orders)

    character_names = [semantic_key(item.name) for item in candidate.characters]
    environment_names = [semantic_key(item.name) for item in candidate.environments]
    if len(set(character_names)) != len(character_names):
        issues.append({"loc": ["characters"], "type": "ambiguous_character_identity", "msg": "Character names must identify one candidate entity each."})
    if len(set(environment_names)) != len(environment_names):
        issues.append({"loc": ["environments"], "type": "ambiguous_environment_identity", "msg": "Environment names must identify one candidate entity each."})

    known_characters = set(character_names)
    known_environments = set(environment_names)
    for scene in candidate.scenes:
        for name in scene.characters:
            if semantic_key(name) not in known_characters:
                issues.append({"loc": ["scenes", scene.scene_order, "characters"], "type": "unknown_character_reference", "msg": f"Unknown character reference: {name[:160]}"})
                failed.add(scene.scene_order)
        if semantic_key(scene.environment) not in known_environments:
            issues.append({"loc": ["scenes", scene.scene_order, "environment"], "type": "unknown_environment_reference", "msg": f"Unknown environment reference: {scene.environment[:160]}"})
            failed.add(scene.scene_order)

    is_delta = bool(request and re.search(r"đồng bằng bắc bộ|đồng bằng sông hồng|châu thổ sông hồng", request.prompt, re.I))
    if is_delta:
        matching_environments = [environment for environment in candidate.environments if environment.region == "NORTHERN_VIETNAM" and environment.subregion == "RED_RIVER_DELTA"]
        if len(candidate.environments) != 1 or len(matching_environments) != 1:
            issues.append({"loc": ["environments"], "type": "red_river_delta_environment_required", "msg": "Use one shared Northern Vietnam / Red River Delta environment for every scene."})
            failed.update(scene.scene_order for scene in candidate.scenes)
        for environment in candidate.environments:
            if environment in matching_environments and environment.terrain.casefold() not in {
                "flat_alluvial_plain", "flat alluvial plain", "đồng bằng phù sa bằng phẳng",
            }:
                issues.append({"loc": ["environments", environment.name, "terrain"], "type": "terrain_not_flat", "msg": "Red River Delta terrain must be flat alluvial plain."})
                failed.update(scene.scene_order for scene in candidate.scenes if semantic_key(scene.environment) == semantic_key(environment.name))
    return issues, sorted(failed)


class CandidateProjectPlanCompiler:
    def __init__(self, allocator: DeterministicTimelineAllocator | None = None):
        self.allocator = allocator or DeterministicTimelineAllocator()

    def compile(self, request: PromptCompilationRequest, candidate: PlannerCandidate, compilation_id: str,
                identity_basis: str) -> tuple[ProjectPlan, dict]:
        issues, failed = validate_candidate_semantics(candidate, request)
        if issues:
            raise CandidateSemanticError(issues, failed)

        suggestions = [scene.suggested_duration_seconds for scene in candidate.scenes]
        weights = [scene.duration_weight for scene in candidate.scenes]
        allocation = self.allocator.allocate(suggestions, request.target_duration_seconds, weights)

        characters_by_key = {semantic_key(item.name): item for item in candidate.characters}
        environments_by_key = {semantic_key(item.name): item for item in candidate.environments}
        character_ids = {
            key: str(uuid5(NAMESPACE_URL, f"phase3b-v3:{identity_basis}:character:{key}"))
            for key in characters_by_key
        }
        environment_ids = {
            key: str(uuid5(NAMESPACE_URL, f"phase3b-v3:{identity_basis}:environment:{key}"))
            for key in environments_by_key
        }
        final_characters = [CharacterReference(
            character_id=character_ids[key], name=item.name, role=item.role, age_group=item.age_group,
            visual_description=item.visual_description, clothing_description=item.clothing_description,
            continuity_constraints=item.continuity_constraints, reference_asset_ids=[], review_status="DRAFT",
        ) for key, item in characters_by_key.items()]

        is_delta_request = bool(re.search(r"đồng bằng bắc bộ|đồng bằng sông hồng|châu thổ sông hồng", request.prompt, re.I))
        required_forbidden = ["núi cao", "làng nhà sàn", "kiến trúc cung điện Trung Hoa", "kiến trúc cung điện Nhật"] if is_delta_request else []
        final_environments = []
        for key, item in environments_by_key.items():
            forbidden = _unique([*item.negative_constraints, *required_forbidden])
            final_environments.append(EnvironmentReference(
                environment_id=environment_ids[key], country=item.country, region=item.region,
                subregion=item.subregion, historical_period=item.historical_period, terrain=item.terrain,
                architecture_profile=item.architecture_profile, visual_description=item.visual_description,
                required_elements=_unique([*item.required_elements, *item.cultural_constraints]), forbidden_elements=forbidden,
                reference_asset_ids=[], review_status="DRAFT",
            ))

        final_scenes = []
        timeline_provenance = []
        for index, scene in enumerate(candidate.scenes):
            order = scene.scene_order
            duration = allocation.durations[index]
            scene_id = str(uuid5(NAMESPACE_URL, f"phase3b-v3:{identity_basis}:scene:{order}:{semantic_key(scene.title)}"))
            env_key = semantic_key(scene.environment)
            env = environments_by_key[env_key]
            characters = _unique(scene.characters)
            character_refs = [character_ids[semantic_key(name)] for name in characters]
            negative = _unique([*scene.negative_constraints, *env.negative_constraints, *required_forbidden])
            final_scenes.append(ScenePlan(
                scene_id=scene_id, scene_number=order, title=scene.title,
                duration_seconds=duration, narration_vi=scene.narration_text,
                learning_purpose=scene.narrative_purpose, environment_id=environment_ids[env_key],
                character_ids=character_refs, visual_action=scene.visual_description,
                camera_shot=("WIDE", "MEDIUM", "CLOSE_UP", "WIDE")[((order - 1) % 4)],
                camera_motion="STATIC", motion_description="Chuyển động nhẹ, phù hợp hoạt hình giáo dục.",
                positive_prompt_draft=", ".join(_unique([scene.visual_description, *scene.cultural_constraints, *env.cultural_constraints])),
                negative_prompt_draft=", ".join(negative), sound_effects=[], music_mood="Nhẹ nhàng, tích cực",
                transition_out="FADE" if order == len(candidate.scenes) else "CUT",
                source_reference_ids=[], grounding_status=("NEEDS_REVIEW" if candidate.grounding_status == "NEEDS_REVIEW" or is_historical_content(request.prompt) else "PENDING"),
            ))
            detail = dict(allocation.provenance[index])
            detail["scene_id"] = scene_id
            timeline_provenance.append(detail)

        grounding_status = "NEEDS_REVIEW" if candidate.grounding_status == "NEEDS_REVIEW" or is_historical_content(request.prompt) else "PENDING"
        plan = ProjectPlan(
            compilation_id=compilation_id, title=candidate.title, learning_objective=candidate.learning_objective,
            subject=request.subject, education_level=request.education_level, language=request.language,
            target_duration_seconds=request.target_duration_seconds, aspect_ratio=request.aspect_ratio,
            visual_style_profile_id=request.requested_style_profile,
            cultural_profile_id=request.requested_cultural_profile or ("red-river-delta-v1" if is_delta_request else None),
            grounding_status=grounding_status, governance_status="DRAFT", release_eligible=False,
            characters=final_characters, environments=final_environments, scenes=final_scenes,
        )
        provenance = {
            "allocator_version": allocation.allocator_version,
            "target_duration_seconds": request.target_duration_seconds,
            "adjusted": any(item["adjusted"] for item in timeline_provenance),
            "scenes": timeline_provenance,
        }
        return plan, provenance


def _unique(values: list[str]) -> list[str]:
    result = []
    seen = set()
    for value in values:
        key = semantic_key(value)
        if key not in seen:
            result.append(value)
            seen.add(key)
    return result
