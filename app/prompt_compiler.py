"""Local deterministic prompt compilation. Prompts are treated only as text data."""
from __future__ import annotations

import hashlib
import json
import os
import re
from decimal import Decimal
from datetime import UTC, datetime
from typing import Any, Literal, Protocol
from uuid import NAMESPACE_URL, uuid4, uuid5

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.timeline_allocator import TIMELINE_ALLOCATOR_VERSION

SCHEMA_VERSION = "1.0"
PLANNER_VERSION = "1.0"
CULTURAL_PROFILE_VERSION = "1"
MAX_PROMPT_LENGTH = int(os.getenv("PROMPT_COMPILER_MAX_LENGTH", "10000"))
MIN_TARGET_DURATION_SECONDS = int(os.getenv("PROMPT_COMPILER_MIN_DURATION", "15"))
MAX_TARGET_DURATION_SECONDS = int(os.getenv("PROMPT_COMPILER_MAX_DURATION", "120"))
DURATION_TOLERANCE_SECONDS = float(os.getenv("PROMPT_COMPILER_DURATION_TOLERANCE", "0.01"))


def is_historical_content(prompt: str) -> bool:
    curricular_mention = re.search(r"môn\s+lịch sử(?:\s+và\s+địa lí)?", prompt, re.I)
    return bool(re.search(r"triều đại|kháng chiến|thế kỷ|năm \d{3,4}|thời (?:lý|trần|lê|nguyễn|hùng vương)|kể chuyện lịch sử", prompt, re.I)) or (bool(re.search("lịch sử", prompt, re.I)) and not curricular_mention)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class PromptCompilationRequest(StrictModel):
    prompt: str = Field(min_length=1, max_length=MAX_PROMPT_LENGTH)
    target_duration_seconds: int = Field(default=45, ge=MIN_TARGET_DURATION_SECONDS, le=MAX_TARGET_DURATION_SECONDS)
    language: str = "vi-VN"
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"
    education_level: Literal["GRADE_1", "GRADE_2", "GRADE_3", "GRADE_4", "GRADE_5"] = "GRADE_4"
    subject: Literal["HISTORY_GEOGRAPHY", "SCIENCE", "LITERATURE", "CIVICS", "OTHER"] = "HISTORY_GEOGRAPHY"
    mode: Literal["AUTO_STORYBOARD", "EXPLICIT_SCENES"] = "AUTO_STORYBOARD"
    requested_style_profile: str | None = None
    requested_cultural_profile: str | None = None

    @field_validator("prompt")
    @classmethod
    def trim_nonempty_prompt(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("prompt must not be empty")
        return value

    @field_validator("language")
    @classmethod
    def supported_language(cls, value: str) -> str:
        if value != "vi-VN":
            raise ValueError("language must be vi-VN in Phase 3A")
        return value

    @field_validator("requested_style_profile", "requested_cultural_profile")
    @classmethod
    def valid_profile_key(cls, value: str | None) -> str | None:
        if value is not None and (not value.strip() or len(value) > 120):
            raise ValueError("profile identifier must be a nonempty string of at most 120 characters")
        return value


class CharacterReference(StrictModel):
    character_id: str
    name: str
    role: str
    age_group: str
    visual_description: str
    clothing_description: str
    continuity_constraints: list[str] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)
    review_status: Literal["DRAFT"] = "DRAFT"


class EnvironmentReference(StrictModel):
    environment_id: str
    country: str
    region: str
    subregion: str
    historical_period: str
    terrain: str
    architecture_profile: str
    visual_description: str
    required_elements: list[str] = Field(default_factory=list)
    forbidden_elements: list[str] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)
    review_status: Literal["DRAFT"] = "DRAFT"


class RegionalEnvironmentProfile(StrictModel):
    regional_environment_profile_id: str
    canonical_region_key: str
    display_name: str
    country: str
    terrain: str
    cultural_profile_version: str
    required_features: list[str] = Field(default_factory=list)
    forbidden_features: list[str] = Field(default_factory=list)
    review_state: Literal["DRAFT", "PENDING", "NEEDS_REVIEW"] = "PENDING"


class SceneLocation(StrictModel):
    scene_location_id: str
    name: str
    normalized_location_key: str
    regional_environment_profile_id: str
    review_state: Literal["DRAFT", "PENDING", "NEEDS_REVIEW"] = "PENDING"


class ScenePlan(StrictModel):
    scene_id: str
    scene_number: int = Field(ge=1)
    title: str
    duration_seconds: int = Field(ge=3, le=8)
    narration_vi: str = Field(min_length=1)
    learning_purpose: str
    environment_id: str
    character_ids: list[str]
    visual_action: str
    camera_shot: Literal["WIDE", "MEDIUM", "CLOSE_UP", "AERIAL"]
    camera_motion: Literal["STATIC", "PAN_LEFT", "PAN_RIGHT", "ZOOM_IN", "ZOOM_OUT"]
    motion_description: str
    positive_prompt_draft: str
    negative_prompt_draft: str
    sound_effects: list[str]
    music_mood: str
    transition_out: Literal["CUT", "FADE", "DISSOLVE"]
    source_reference_ids: list[str]
    grounding_status: Literal["PENDING", "GROUNDED", "NEEDS_REVIEW"]
    content_review_status: Literal["PENDING", "APPROVED", "REJECTED"] = "PENDING"
    cultural_review_status: Literal["PENDING", "APPROVED", "REJECTED"] = "PENDING"
    keyframe_status: Literal["NOT_GENERATED", "GENERATED"] = "NOT_GENERATED"
    locked: bool = False

    @model_validator(mode="after")
    def require_source_for_grounded_status(self):
        for field_name in ("scene_id", "title", "narration_vi", "learning_purpose", "environment_id", "visual_action"):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")
        if not self.source_reference_ids and self.grounding_status == "GROUNDED":
            raise ValueError("scene without source_reference_ids cannot be GROUNDED")
        return self


class ProjectPlan(StrictModel):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    compilation_id: str
    title: str
    learning_objective: str
    subject: str
    education_level: str
    language: str
    target_duration_seconds: int
    aspect_ratio: str
    visual_style_profile_id: str | None
    cultural_profile_id: str | None
    grounding_status: Literal["PENDING", "GROUNDED", "NEEDS_REVIEW"]
    governance_status: Literal["DRAFT"] = "DRAFT"
    release_eligible: Literal[False] = False
    characters: list[CharacterReference]
    environments: list[EnvironmentReference]
    scenes: list[ScenePlan]
    regional_environment_profile: RegionalEnvironmentProfile | None = None
    scene_locations: list[SceneLocation] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references_and_scene_sequence(self):
        if not self.title.strip() or not self.learning_objective.strip():
            raise ValueError("title and learning_objective must not be empty")
        if not self.scenes:
            raise ValueError("plan must contain at least one scene")
        numbers = [s.scene_number for s in self.scenes]
        if numbers != list(range(1, len(numbers) + 1)):
            raise ValueError("scene_number values must be unique, continuous, and ordered")
        character_ids = {c.character_id for c in self.characters}
        environment_ids = {e.environment_id for e in self.environments}
        location_ids = {location.scene_location_id for location in self.scene_locations}
        if len(character_ids) != len(self.characters):
            raise ValueError("character_id values must be unique")
        if len(environment_ids) != len(self.environments):
            raise ValueError("environment_id values must be unique")
        if len(location_ids) != len(self.scene_locations):
            raise ValueError("scene_location_id values must be unique")
        if self.regional_environment_profile:
            profile_id = self.regional_environment_profile.regional_environment_profile_id
            if any(location.regional_environment_profile_id != profile_id for location in self.scene_locations):
                raise ValueError("all scene locations must reference the regional environment profile")
        scene_ids = [s.scene_id for s in self.scenes]
        if len(set(scene_ids)) != len(scene_ids):
            raise ValueError("scene_id values must be unique")
        for scene in self.scenes:
            if scene.environment_id not in environment_ids:
                raise ValueError("scene references missing environment_id")
            if not set(scene.character_ids) <= character_ids:
                raise ValueError("scene references missing character_id")
            for text in (scene.positive_prompt_draft, scene.negative_prompt_draft):
                if re.search(r"(?:[A-Za-z]:\\|/[^\s]+|\b[A-Za-z0-9_.-]+\.(?:safetensors|ckpt|pt|png|jpg|jpeg)\b|\b(?:SDXL|Qwen|Ollama|ComfyUI)\b)", text, re.I):
                    raise ValueError("prompt drafts must not contain model names or file paths")
        if abs(sum(s.duration_seconds for s in self.scenes) - self.target_duration_seconds) > DURATION_TOLERANCE_SECONDS:
            raise ValueError(f"scene durations must sum to target duration within {DURATION_TOLERANCE_SECONDS} seconds")
        return self


def validate_compiled_plan(request: PromptCompilationRequest, plan: ProjectPlan) -> list[str]:
    """Deterministic business checks applied to every planner's output."""
    errors: list[str] = []
    if plan.target_duration_seconds != request.target_duration_seconds:
        errors.append("plan target duration does not match request")
    if plan.language != request.language or plan.aspect_ratio != request.aspect_ratio:
        errors.append("plan language/aspect ratio does not match request")
    if plan.subject != request.subject or plan.education_level != request.education_level:
        errors.append("plan subject/education level does not match request")
    if plan.visual_style_profile_id != request.requested_style_profile:
        errors.append("plan visual style profile must match the requested profile")
    if request.requested_cultural_profile and plan.cultural_profile_id != request.requested_cultural_profile:
        errors.append("plan cultural profile does not match requested profile")
    if plan.governance_status != "DRAFT" or plan.release_eligible:
        errors.append("planner output must remain DRAFT and release-ineligible")
    if any(scene.source_reference_ids for scene in plan.scenes):
        errors.append("planner invented source references; no source IDs were provided")
    if plan.grounding_status == "GROUNDED" or any(s.grounding_status == "GROUNDED" for s in plan.scenes):
        errors.append("grounded status requires supplied, validated reference sources")
    if any(s.locked or s.content_review_status != "PENDING" or s.cultural_review_status != "PENDING" or s.keyframe_status != "NOT_GENERATED" for s in plan.scenes):
        errors.append("planner output cannot approve, lock, or generate keyframes")
    for value in plan.model_dump_json().split('"'):
        if re.search(r"(?:[A-Za-z]:\\|/(?:[^\s/]+/)+[^\s]*|\b\w+\.(?:safetensors|ckpt|pt|gguf)\b|\b(?:Qwen|Ollama|ComfyUI|SDXL|LoRA)\b)", value, re.I):
            errors.append("planner output contains a model identifier or local file path")
            break
    prompt = request.prompt
    delta_context = bool(re.search(r"đồng bằng bắc bộ|đồng bằng sông hồng|châu thổ sông hồng", prompt, re.I))
    if delta_context:
        if request.target_duration_seconds == 45:
            if not 7 <= len(plan.scenes) <= 10:
                errors.append("45-second Red River Delta plan must contain 7–10 scenes")
            if sum((Decimal(str(scene.duration_seconds)) for scene in plan.scenes), Decimal("0")) != Decimal("45"):
                errors.append("45-second Red River Delta scene durations must total exactly 45 seconds")
            if any(not 3 <= scene.duration_seconds <= 8 for scene in plan.scenes):
                errors.append("45-second Red River Delta scenes must each be 3–8 seconds")
        delta_envs = [env for env in plan.environments if env.region == "NORTHERN_VIETNAM" and env.subregion == "RED_RIVER_DELTA"]
        profile = plan.regional_environment_profile
        if profile is None or profile.canonical_region_key != "red-river-delta":
            errors.append("specific Red River Delta request requires canonical regional environment profile")
        if not delta_envs:
            errors.append("specific Red River Delta request requires compatible scene environments")
        else:
            if any(env.terrain.casefold() not in {"flat_alluvial_plain", "flat alluvial plain", "alluvial plain, flat", "flat_delta"} for env in delta_envs):
                errors.append("Red River Delta terrain must be FLAT_ALLUVIAL_PLAIN")
            required_forbidden = {"núi cao", "làng nhà sàn", "kiến trúc cung điện trung hoa", "kiến trúc cung điện nhật"}
            for environment in delta_envs:
                forbidden = {item.casefold() for item in environment.forbidden_elements}
                if not required_forbidden <= forbidden:
                    errors.append("Red River Delta environment omits required forbidden visual patterns")
                    break
            location_ids = {location.scene_location_id for location in plan.scene_locations}
            if not plan.scene_locations or any(scene.environment_id not in {env.environment_id for env in delta_envs} for scene in plan.scenes):
                errors.append("Red River Delta scenes require compatible scene locations")
            if profile and any(location.regional_environment_profile_id != profile.regional_environment_profile_id for location in plan.scene_locations):
                errors.append("scene locations must inherit the canonical regional environment profile")
            if len({character.character_id for character in plan.characters if sum(character.character_id in scene.character_ids for scene in plan.scenes) >= 2}) < 1:
                errors.append("at least one stable character ID must be reused across scenes")
        if request.requested_cultural_profile and plan.cultural_profile_id != request.requested_cultural_profile:
            errors.append("plan cultural profile does not match requested profile")
    if is_historical_content(prompt) and plan.grounding_status != "NEEDS_REVIEW":
        if not re.search(r"(thế kỷ|năm \d{3,4}|thời (?:lý|trần|lê|nguyễn|hùng vương))", prompt, re.I) or not re.search(r"(tại|ở|vùng|thành|kinh đô)\s+\S+|thăng long|hoa lư|cổ loa|huế|điện biên", prompt, re.I):
            errors.append("historical content without period/location must be marked NEEDS_REVIEW")
    regional_match = bool(re.search(r"đồng bằng bắc bộ|đồng bằng sông hồng|châu thổ sông hồng", prompt, re.I))
    vague_north_match = bool(re.search(r"bắc bộ|miền bắc|tây bắc", prompt, re.I)) and not regional_match
    if (re.search(r"việt nam", prompt, re.I) and not regional_match or vague_north_match) and plan.grounding_status != "NEEDS_REVIEW":
        errors.append("regionally vague Vietnam prompt must be marked NEEDS_REVIEW")
    conflict = regional_match and bool(re.search(r"miền nam|tây nguyên|nhà sàn|cung điện trung hoa|kiến trúc nhật", prompt, re.I))
    if conflict and plan.grounding_status != "NEEDS_REVIEW":
        errors.append("conflicting regional cues must be marked NEEDS_REVIEW")
    if request.mode == "EXPLICIT_SCENES":
        entries = list(re.finditer(r"(?im)^\s*(?:cảnh|scene)\s*(\d+)\s*[:.)-]?\s*(.*)$", prompt))
        if len(entries) != len(plan.scenes):
            errors.append("explicit scene count/order was not preserved")
        else:
            for entry, scene in zip(entries, plan.scenes):
                body = (entry.group(2) + " " + prompt[entry.end():(entries[entries.index(entry) + 1].start() if entries.index(entry) + 1 < len(entries) else len(prompt))]).casefold()
                expected = {word for word in re.findall(r"[\wÀ-ỹ]+", body) if len(word) > 3}
                actual = {word for word in re.findall(r"[\wÀ-ỹ]+", f"{scene.title} {scene.narration_vi} {scene.visual_action}".casefold()) if len(word) > 3}
                if expected and len(expected & actual) / len(expected) < 0.2:
                    errors.append("explicit scene meaning/order may not have been preserved")
                    break
    return errors


class PromptPlanner(Protocol):
    name: str
    version: str
    def identity(self) -> dict[str, Any]: ...
    def compile(self, request: PromptCompilationRequest, compilation_id: str) -> ProjectPlan: ...


_DEFAULT_SCENES = [
    ("Mở đầu", "Thiên nhiên quanh em", "Khơi gợi quan sát", "Hãy cùng quan sát thiên nhiên quanh mình và nghĩ xem vì sao cần gìn giữ môi trường sống.", "Toàn cảnh dòng sông và cánh đồng lúa dưới nắng sớm.", "WIDE"),
    ("Quan sát dòng sông", "Nguồn nước", "Nhận biết vai trò của sông", "Dòng sông mang nước đến cho con người, cây cối và nhiều loài sinh vật.", "Dòng sông chảy bên bờ xanh, học sinh quan sát từ lối đi an toàn.", "MEDIUM"),
    ("Bên ruộng lúa", "Ruộng lúa", "Liên hệ thiên nhiên với đời sống", "Những thửa ruộng màu mỡ cần đất và nước sạch để cây lúa phát triển.", "Ruộng lúa trải rộng trên đồng bằng, bờ ruộng nhỏ và kênh dẫn nước.", "WIDE"),
    ("Cùng nhặt rác", "Giữ gìn nơi công cộng", "Thực hành hành động bảo vệ môi trường", "Các bạn thu gom rác đúng cách để đường làng và bờ sông sạch đẹp.", "Học sinh đeo găng, dùng kẹp gắp rác vào túi phân loại.", "MEDIUM"),
    ("Trồng thêm cây", "Cây xanh", "Khuyến khích chăm sóc cây", "Mỗi cây xanh được chăm sóc tốt góp phần làm nơi ở thêm trong lành.", "Học sinh trồng cây non bên sân trường, tưới nước vừa đủ.", "MEDIUM"),
    ("Bảo vệ nguồn nước", "Nước sạch", "Nêu trách nhiệm cộng đồng", "Người dân cùng giữ nguồn nước sạch và không xả rác xuống dòng sông.", "Người dân nhắc nhau giữ sạch bờ sông và thu gom rác đúng nơi.", "WIDE"),
    ("Việc tốt mỗi ngày", "Trách nhiệm chung", "Củng cố lựa chọn hành động", "Khi mọi người cùng góp sức, dòng sông và đồng ruộng được chăm sóc tốt hơn.", "Học sinh và người dân cùng chăm cây bên con đường sạch.", "WIDE"),
    ("Thông điệp", "Bảo vệ thiên nhiên", "Ghi nhớ thông điệp", "Hãy bắt đầu từ việc nhỏ hôm nay để bảo vệ thiên nhiên cho ngày mai.", "Nhóm học sinh nhìn về dòng sông và ruộng lúa xanh, khung hình sáng ấm.", "CLOSE_UP"),
]


class DeterministicMockPromptPlanner:
    name = "DeterministicMockPromptPlanner"
    version = PLANNER_VERSION

    def identity(self) -> dict[str, Any]:
        return {"provider": "mock", "model": None, "resolved_digest": "mock-deterministic-v1",
                "template_version": "mock-template-v1"}

    def compile(self, request: PromptCompilationRequest, compilation_id: str) -> ProjectPlan:
        prompt = request.prompt
        historic = is_historical_content(prompt)
        delta_specific = bool(re.search(r"đồng bằng bắc bộ|đồng bằng sông hồng|châu thổ sông hồng", prompt, re.I))
        regional = delta_specific
        vague_vietnam = bool(re.search(r"việt nam", prompt, re.I)) and not regional
        vague_north = bool(re.search(r"bắc bộ|miền bắc|tây bắc", prompt, re.I)) and not delta_specific
        warnings = []
        grounding = "PENDING"
        period_match = re.search(r"(thế kỷ\s+[\w]+|năm\s+\d{3,4}|thời\s+(?:lý|trần|lê|nguyễn|hùng vương))", prompt, re.I)
        period = period_match.group(1) if period_match else ("UNSPECIFIED" if historic else "CONTEMPORARY")
        region, subregion = "VIETNAM_GENERIC", "VIETNAM_GENERIC"
        if regional:
            region, subregion = "NORTHERN_VIETNAM", "RED_RIVER_DELTA"
        if historic and not re.search(r"(thế kỷ|năm \d{3,4}|thời (?:lý|trần|lê|nguyễn|hùng vương))", prompt, re.I):
            grounding = "NEEDS_REVIEW"; warnings.append("Historical content lacks a specified period; do not infer period, clothing, or architecture.")
        if historic and not re.search(r"(tại|ở|vùng|thành|kinh đô)\s+[A-ZÀ-ỸĐ][\wÀ-ỹ-]+|thăng long|hoa lư|cổ loa|huế|điện biên", prompt, re.I):
            grounding = "NEEDS_REVIEW"; warnings.append("Historical content lacks a specified location; do not infer a historical setting.")
        if vague_vietnam:
            grounding = "NEEDS_REVIEW"; warnings.append("Prompt says Vietnam without a specific region; regional grounding is required.")
        if vague_north:
            grounding = "NEEDS_REVIEW"; warnings.append("Northern Vietnam is named without a sufficiently specific subregion; do not assume the Red River Delta.")
        if (regional or vague_north) and re.search(r"(miền nam|tây nguyên|nhà sàn|cung điện trung hoa|kiến trúc nhật)", prompt, re.I):
            grounding = "NEEDS_REVIEW"; warnings.append("Prompt contains potentially conflicting regional or period cues.")
        if regional:
            cultural_id = request.requested_cultural_profile or "red-river-delta-v1"
            env = EnvironmentReference(environment_id="red-river-delta-rural-v1", country="VIETNAM", region=region, subregion=subregion,
                historical_period=period, terrain="FLAT_ALLUVIAL_PLAIN", architecture_profile="NORTHERN_VIETNAMESE_RURAL",
                visual_description="Đồng bằng Bắc Bộ đương đại với ruộng lúa thấp, bờ sông và lối đi nông thôn.",
                required_elements=["dòng sông", "ruộng lúa"], forbidden_elements=["núi cao", "làng nhà sàn", "kiến trúc cung điện Trung Hoa", "kiến trúc cung điện Nhật"])
        else:
            cultural_id = request.requested_cultural_profile
            env = EnvironmentReference(environment_id="vietnam-context-needs-review-v1", country="VIETNAM", region=region, subregion=subregion,
                historical_period=period, terrain="UNSPECIFIED", architecture_profile="UNSPECIFIED",
                visual_description="Bối cảnh cần được xác minh trước khi tạo hình.", required_elements=[], forbidden_elements=[])
        extracted = []
        if request.mode == "EXPLICIT_SCENES":
            matches = list(re.finditer(r"(?im)^\s*(?:cảnh|scene)\s*(\d+)\s*[:.)-]?\s*(.*)$", prompt))
            if not matches:
                raise ValueError("EXPLICIT_SCENES requires numbered Cảnh 1, Cảnh 2, ... entries")
            for i, match in enumerate(matches):
                start = match.end(); end = matches[i + 1].start() if i + 1 < len(matches) else len(prompt)
                body = " ".join([match.group(2), prompt[start:end]]).strip()
                extracted.append((match.group(1), body))
            if [int(n) for n, _ in extracted] != list(range(1, len(extracted) + 1)):
                raise ValueError("explicit scene numbers must be continuous and ordered")
            items = [(f"Cảnh {i+1}", "Nội dung người dùng", "Thực hiện ý cảnh đã nêu", body, body, "MEDIUM") for i, (_, body) in enumerate(extracted)]
        else:
            items = _DEFAULT_SCENES
        count = len(items)
        if not 3 <= request.target_duration_seconds / count <= 8:
            raise ValueError("target duration and scene count cannot satisfy 3–8 second scene limits")
        base, remainder = divmod(request.target_duration_seconds, count)
        durations = [base + (1 if i < remainder else 0) for i in range(count)]
        scenes = []
        for i, ((title, topic, purpose, narration, action, shot), duration) in enumerate(zip(items, durations)):
            scenes.append(ScenePlan(scene_id=str(uuid5(NAMESPACE_URL, f"{compilation_id}:scene:{i + 1}")), scene_number=i + 1, title=title, duration_seconds=duration,
                narration_vi=narration, learning_purpose=purpose, environment_id=env.environment_id,
                character_ids=["student-lan-v1", "community-member-v1"], visual_action=action,
                camera_shot=shot, camera_motion="STATIC", motion_description="Chuyển động nhẹ, nhịp chậm, phù hợp hoạt hình giáo dục.",
                positive_prompt_draft=f"Hoạt hình giáo dục 2D, lớp 4, {action}",
                negative_prompt_draft="Không chữ trong hình, không núi cao, không nhà sàn, không cung điện ngoại quốc.",
                sound_effects=[], music_mood="Ấm áp, khích lệ", transition_out="DISSOLVE" if i < count - 1 else "FADE",
                source_reference_ids=[], grounding_status="NEEDS_REVIEW" if grounding == "NEEDS_REVIEW" else "PENDING"))
        title = "Bảo vệ thiên nhiên" if re.search(r"bảo vệ thiên nhiên", prompt, re.I) else "Storyboard giáo dục"
        plan = ProjectPlan(compilation_id=compilation_id, title=title,
            learning_objective="Nhận biết giá trị của thiên nhiên và nêu hành động thiết thực để bảo vệ môi trường.",
            subject=request.subject, education_level=request.education_level, language=request.language,
            target_duration_seconds=request.target_duration_seconds, aspect_ratio=request.aspect_ratio,
            visual_style_profile_id=request.requested_style_profile, cultural_profile_id=cultural_id,
            grounding_status=grounding,
            characters=[CharacterReference(character_id="student-lan-v1", name="Lan", role="STUDENT", age_group="PRIMARY_SCHOOL",
                visual_description="Học sinh tiểu học vui vẻ, phong cách hoạt hình 2D, không dựa trên người thật.",
                clothing_description="Đồng phục học sinh phổ thông, màu sắc giản dị.", continuity_constraints=["Giữ nguyên kiểu tóc và trang phục giữa các cảnh."]),
                CharacterReference(character_id="community-member-v1", name="Người dân", role="COMMUNITY_MEMBER", age_group="ADULT",
                visual_description="Người dân địa phương đương đại, diện mạo thân thiện và đa dạng.", clothing_description="Trang phục sinh hoạt hiện đại, kín đáo, phù hợp hoạt động ngoài trời.")],
            environments=[env], scenes=scenes,
            regional_environment_profile=(RegionalEnvironmentProfile(
                regional_environment_profile_id="mock-red-river-delta-profile-v1", canonical_region_key="red-river-delta",
                display_name="Đồng bằng Bắc Bộ", country="Vietnam", terrain="flat_delta",
                cultural_profile_version=cultural_id or "v1", required_features=["dòng sông", "ruộng lúa"],
                forbidden_features=env.forbidden_elements, review_state="NEEDS_REVIEW" if grounding == "NEEDS_REVIEW" else "PENDING"
            ) if regional else None),
            scene_locations=([SceneLocation(scene_location_id=env.environment_id, name="Đồng bằng Bắc Bộ",
                normalized_location_key="đồng bằng bắc bộ", regional_environment_profile_id="mock-red-river-delta-profile-v1",
                review_state="NEEDS_REVIEW" if grounding == "NEEDS_REVIEW" else "PENDING")] if regional else []))
        return plan


def normalized_request(request: PromptCompilationRequest) -> dict:
    result = request.model_dump(mode="json")
    result["prompt"] = " ".join(request.prompt.split())
    return result


def request_digest(request: PromptCompilationRequest, planner: PromptPlanner, cultural_profile_version: str = CULTURAL_PROFILE_VERSION,
                   identity: dict[str, Any] | None = None) -> str:
    identity = identity or (planner.identity() if hasattr(planner, "identity") else {"provider": "mock", "resolved_digest": planner.version})
    hash_identity = {key: identity.get(key) for key in ("provider", "resolved_digest", "template_version", "seed", "temperature")}
    material = {"request": normalized_request(request), "planner_type": planner.name, "planner_version": planner.version,
                "planner_identity": hash_identity,
                "schema_version": SCHEMA_VERSION, "cultural_profile_version": cultural_profile_version,
                "timeline_allocator_version": TIMELINE_ALLOCATOR_VERSION}
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
