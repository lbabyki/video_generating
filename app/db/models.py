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
