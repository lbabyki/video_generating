from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LoRARegistryEntry(Base):
    __tablename__ = "lora_registry"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    base_model: Mapped[str] = mapped_column(String(120))
    revision: Mapped[str] = mapped_column(String(160))
    sha256: Mapped[str] = mapped_column(String(64), unique=True)
    source_url: Mapped[str] = mapped_column(Text)
    license: Mapped[str] = mapped_column(String(160))
    weight: Mapped[float] = mapped_column(Float, default=0.7)
    file_name: Mapped[str] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    state: Mapped[str] = mapped_column(String(16), default="DRAFT")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ModelRegistryEntry(Base):
    __tablename__ = "model_registry"
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    model_type: Mapped[str] = mapped_column(String(32), nullable=False)
    architecture: Mapped[str] = mapped_column(String(64), nullable=False)
    source_repository: Mapped[str] = mapped_column(String(240), nullable=False)
    source_revision: Mapped[str] = mapped_column(String(64), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    local_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    format: Mapped[str] = mapped_column(String(32), nullable=False)
    compatible_workflow: Mapped[str] = mapped_column(String(120), nullable=False)
    license_id: Mapped[str] = mapped_column(String(120), nullable=False)
    license_url: Mapped[str] = mapped_column(Text, nullable=False)
    license_review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    commercial_use: Mapped[str] = mapped_column(String(64), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class VisualStyleProfile(Base):
    __tablename__ = "visual_style_profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    version: Mapped[int] = mapped_column(Integer, default=1)
    state: Mapped[str] = mapped_column(String(16), default="DRAFT")
    prompt_prefix: Mapped[str] = mapped_column(Text)
    negative_prompt: Mapped[str] = mapped_column(Text, default="")
    aspect_ratio: Mapped[str] = mapped_column(String(16), default="16:9")
    lora_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("name", "version", name="uq_profile_name_version"),)


class VisualStyleProfileLoRA(Base):
    __tablename__ = "visual_style_profile_loras"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    profile_id: Mapped[str] = mapped_column(ForeignKey("visual_style_profiles.id", ondelete="CASCADE"), nullable=False)
    lora_id: Mapped[str] = mapped_column(ForeignKey("lora_registry.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    model_strength: Mapped[float] = mapped_column(Float, nullable=False)
    clip_strength: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("profile_id", "position", name="uq_profile_lora_position"),)


class CulturalProfile(Base):
    __tablename__ = "cultural_profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(16), nullable=False, default="DRAFT")
    guidance: Mapped[str] = mapped_column(Text, nullable=False)
    __table_args__ = (UniqueConstraint("name", "version", name="uq_cultural_profile_version"),)


class ReferenceSource(Base):
    __tablename__ = "reference_sources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    provenance: Mapped[str] = mapped_column(Text, nullable=False)
    license: Mapped[str] = mapped_column(String(240), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(240), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="FACTUAL_REFERENCE")
    local_file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    access_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    page_or_section: Mapped[str | None] = mapped_column(String(240), nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    mime_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    usage_permission: Mapped[str] = mapped_column(String(32), nullable=False, default="UNKNOWN")
    attribution: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")


class DatasetAssetReview(Base):
    __tablename__ = "dataset_asset_reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str] = mapped_column(ForeignKey("reference_sources.id"), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(240), nullable=False)
    intended_use: Mapped[str] = mapped_column(String(120), nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")


class SceneGovernance(Base):
    __tablename__ = "scene_governance"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    content_review: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    cultural_review: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    cultural_profile_id: Mapped[str | None] = mapped_column(ForeignKey("cultural_profiles.id"), nullable=True)


class PromptCompilationRecord(Base):
    __tablename__ = "prompt_compilations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_request_json: Mapped[str] = mapped_column(Text, nullable=False)
    planner_type: Mapped[str] = mapped_column(String(120), nullable=False)
    planner_version: Mapped[str] = mapped_column(String(32), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(16), nullable=False)
    cultural_profile_version: Mapped[str] = mapped_column(String(32), nullable=False)
    plan_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_warnings_json: Mapped[str] = mapped_column(Text, nullable=False)
    governance_state: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    compilation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUCCEEDED")
    planner_provider: Mapped[str] = mapped_column(String(32), nullable=False, default="mock")
    planner_model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    resolved_model_digest: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_template_version: Mapped[str] = mapped_column(String(80), nullable=False, default="mock-template-v1")
    repair_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    validation_errors_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    resource_metrics_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    planner_seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planner_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validation_result_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    validation_stage: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_scene_orders_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    candidate_response_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    candidate_diagnostic_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeline_provenance_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("request_hash", name="uq_prompt_compilations_request_hash"),)


class PromptModelProvenance(Base):
    __tablename__ = "prompt_model_provenance"
    resolved_model_digest: Mapped[str] = mapped_column(String(128), primary_key=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    ollama_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    requested_tag: Mapped[str] = mapped_column(String(160), nullable=False)
    quantization: Mapped[str | None] = mapped_column(String(64), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    architecture: Mapped[str | None] = mapped_column(String(120), nullable=True)
    parameter_size: Mapped[str | None] = mapped_column(String(80), nullable=True)
    license: Mapped[str] = mapped_column(String(80), nullable=False)
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    prompt_template_version: Mapped[str] = mapped_column(String(80), nullable=False)


class VisualBibleSet(Base):
    __tablename__ = "visual_bible_sets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(120), nullable=False)
    compilation_id: Mapped[str] = mapped_column(ForeignKey("prompt_compilations.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="DRAFT")
    source_plan_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    cultural_profile_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cultural_profile_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (UniqueConstraint("compilation_id", "version", name="uq_visual_bible_compilation_version"),)


class CharacterBible(Base):
    __tablename__ = "character_bibles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bible_set_id: Mapped[str] = mapped_column(ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    character_id: Mapped[str] = mapped_column(String(120), nullable=False)
    semantic_key: Mapped[str] = mapped_column(String(160), nullable=False)
    display_name: Mapped[str] = mapped_column(String(240), nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    age_band: Mapped[str] = mapped_column(String(120), nullable=False)
    gender_presentation: Mapped[str | None] = mapped_column(String(120), nullable=True)
    body_proportion_style: Mapped[str] = mapped_column(Text, nullable=False)
    face_description: Mapped[str] = mapped_column(Text, nullable=False)
    hairstyle: Mapped[str] = mapped_column(Text, nullable=False)
    wardrobe: Mapped[str] = mapped_column(Text, nullable=False)
    footwear: Mapped[str] = mapped_column(Text, nullable=False)
    accessories: Mapped[str] = mapped_column(Text, nullable=False)
    primary_palette: Mapped[str] = mapped_column(Text, nullable=False)
    secondary_palette: Mapped[str] = mapped_column(Text, nullable=False)
    expression_range: Mapped[str] = mapped_column(Text, nullable=False)
    pose_guidance: Mapped[str] = mapped_column(Text, nullable=False)
    cultural_notes: Mapped[str] = mapped_column(Text, nullable=False)
    forbidden_variations: Mapped[str] = mapped_column(Text, nullable=False)
    reference_asset_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    review_status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    provenance: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class EnvironmentBible(Base):
    __tablename__ = "environment_bibles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bible_set_id: Mapped[str] = mapped_column(ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    environment_id: Mapped[str] = mapped_column(String(120), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(240), nullable=False)
    regional_profile_id: Mapped[str] = mapped_column(String(120), nullable=False)
    terrain: Mapped[str] = mapped_column(String(120), nullable=False)
    architecture_guidance: Mapped[str] = mapped_column(Text, nullable=False)
    vegetation_guidance: Mapped[str] = mapped_column(Text, nullable=False)
    water_features: Mapped[str] = mapped_column(Text, nullable=False)
    road_path_guidance: Mapped[str] = mapped_column(Text, nullable=False)
    season: Mapped[str] = mapped_column(String(120), nullable=False)
    weather: Mapped[str] = mapped_column(String(240), nullable=False)
    time_of_day_options: Mapped[str] = mapped_column(Text, nullable=False)
    lighting: Mapped[str] = mapped_column(Text, nullable=False)
    visual_palette: Mapped[str] = mapped_column(Text, nullable=False)
    cultural_notes: Mapped[str] = mapped_column(Text, nullable=False)
    required_features: Mapped[str] = mapped_column(Text, nullable=False)
    forbidden_features: Mapped[str] = mapped_column(Text, nullable=False)
    grounding_status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    review_status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    provenance: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    reference_asset_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class SceneVisualBinding(Base):
    __tablename__ = "scene_visual_bindings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bible_set_id: Mapped[str] = mapped_column(ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    scene_id: Mapped[str] = mapped_column(String(120), nullable=False)
    character_ids: Mapped[str] = mapped_column(Text, nullable=False)
    location_id: Mapped[str] = mapped_column(String(120), nullable=False)
    regional_profile_id: Mapped[str] = mapped_column(String(120), nullable=False)
    character_bible_version: Mapped[int] = mapped_column(Integer, nullable=False)
    environment_bible_version: Mapped[int] = mapped_column(Integer, nullable=False)
    visual_style_profile_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cultural_profile_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    grounding_status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    source_plan_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    binding_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class VisualPromptPackage(Base):
    __tablename__ = "visual_prompt_packages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bible_set_id: Mapped[str] = mapped_column(ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    scene_id: Mapped[str] = mapped_column(String(120), nullable=False)
    positive_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    character_tokens: Mapped[str] = mapped_column(Text, nullable=False)
    environment_tokens: Mapped[str] = mapped_column(Text, nullable=False)
    composition: Mapped[str] = mapped_column(Text, nullable=False)
    camera_framing: Mapped[str] = mapped_column(String(40), nullable=False)
    lighting: Mapped[str] = mapped_column(Text, nullable=False)
    color_palette: Mapped[str] = mapped_column(Text, nullable=False)
    required_cultural_features: Mapped[str] = mapped_column(Text, nullable=False)
    forbidden_features: Mapped[str] = mapped_column(Text, nullable=False)
    base_model_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    base_model_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    intended_style_lora_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    seed_placeholder: Mapped[str] = mapped_column(String(80), nullable=False, default="UNASSIGNED")
    package_version: Mapped[str] = mapped_column(String(40), nullable=False)
    package_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    governance_status: Mapped[str] = mapped_column(String(16), nullable=False, default="DRAFT")
    release_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    keyframe_status: Mapped[str] = mapped_column(String(32), nullable=False, default="NOT_GENERATED")
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    package_status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    supported_evidence_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    project_design_source_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    excluded_claims: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class GroundingRequirement(Base):
    __tablename__ = "grounding_requirements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bible_set_id: Mapped[str] = mapped_column(ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(120), nullable=False)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    source_reference_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    needs_more_evidence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class GroundingResolution(Base):
    __tablename__ = "grounding_resolutions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bible_set_id: Mapped[str] = mapped_column(ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    requirement_id: Mapped[str] = mapped_column(ForeignKey("grounding_requirements.id", ondelete="CASCADE"), nullable=False, unique=True)
    original_requirement: Mapped[str] = mapped_column(Text, nullable=False)
    factual_evidence_status: Mapped[str] = mapped_column(String(32), nullable=False)
    project_design_evidence: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    supported_scope: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    excluded_claims: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    resolution_mode: Mapped[str] = mapped_column(String(48), nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(120), nullable=False)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class EvidenceLink(Base):
    __tablename__ = "evidence_links"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    grounding_requirement_id: Mapped[str] = mapped_column(ForeignKey("grounding_requirements.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str] = mapped_column(ForeignKey("reference_sources.id"), nullable=False)
    page_or_section: Mapped[str] = mapped_column(String(240), nullable=False)
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    supported_claim: Mapped[str] = mapped_column(Text, nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    review_status: Mapped[str] = mapped_column(String(24), nullable=False, default="PENDING")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class VisualBibleReview(Base):
    __tablename__ = "visual_bible_reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bible_set_id: Mapped[str] = mapped_column(ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    target_type: Mapped[str] = mapped_column(String(24), nullable=False)
    target_id: Mapped[str] = mapped_column(String(120), nullable=False)
    checklist_json: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="PENDING")
    reviewer_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class VisualBibleAudit(Base):
    __tablename__ = "visual_bible_audits"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bible_set_id: Mapped[str] = mapped_column(ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class HumanReviewer(Base):
    __tablename__ = "human_reviewers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provenance: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_by_method: Mapped[str] = mapped_column(String(40), nullable=False, default="local_cli")
    __table_args__ = (UniqueConstraint("display_name", "role", name="uq_human_reviewer_name_role"),)


class HumanReviewerAudit(Base):
    __tablename__ = "human_reviewer_audits"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    reviewer_id: Mapped[str] = mapped_column(ForeignKey("human_reviewers.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
