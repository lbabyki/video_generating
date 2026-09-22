"""Local deterministic prompt compilation. Prompts are treated only as text data."""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import NAMESPACE_URL, uuid4, uuid5

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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
    model_config = ConfigDict(extra="forbid", strict=True)


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


class ScenePlan(StrictModel):
    scene_id: str
    scene_number: int = Field(ge=1)
    title: str
    duration_seconds: float = Field(ge=3, le=8)
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

    @model_validator(mode="after")
    def validate_references_and_scene_sequence(self):
        if not self.scenes:
            raise ValueError("plan must contain at least one scene")
        numbers = [s.scene_number for s in self.scenes]
        if numbers != list(range(1, len(numbers) + 1)):
            raise ValueError("scene_number values must be unique, continuous, and ordered")
        character_ids = {c.character_id for c in self.characters}
        environment_ids = {e.environment_id for e in self.environments}
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


class PromptPlanner(Protocol):
    name: str
    version: str
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
        each = round(request.target_duration_seconds / count, 3)
        durations = [each] * count
        durations[-1] = round(request.target_duration_seconds - sum(durations[:-1]), 3)
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
            environments=[env], scenes=scenes)
        return plan


def normalized_request(request: PromptCompilationRequest) -> dict:
    result = request.model_dump(mode="json")
    result["prompt"] = " ".join(request.prompt.split())
    return result


def request_digest(request: PromptCompilationRequest, planner: PromptPlanner, cultural_profile_version: str = CULTURAL_PROFILE_VERSION) -> str:
    material = {"request": normalized_request(request), "planner_type": planner.name, "planner_version": planner.version,
                "schema_version": SCHEMA_VERSION, "cultural_profile_version": cultural_profile_version}
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
