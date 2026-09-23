"""Add grounded visual bible foundation tables.

Revision ID: 0011_visual_bibles
Revises: 0010_candidate_timeline_observability
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_visual_bibles"
down_revision = "0010_candidate_timeline_observability"
branch_labels = depends_on = None

def upgrade() -> None:
    op.create_table("visual_bible_sets",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(120), nullable=False),
        sa.Column("compilation_id", sa.String(36), sa.ForeignKey("prompt_compilations.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False), sa.Column("status", sa.String(16), nullable=False),
        sa.Column("source_plan_hash", sa.String(64), nullable=False), sa.Column("cultural_profile_id", sa.String(120)),
        sa.Column("cultural_profile_version", sa.String(32)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True)), sa.Column("locked_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("compilation_id", "version", name="uq_visual_bible_compilation_version"))
    common_fk = lambda table: sa.Column("bible_set_id", sa.String(36), sa.ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False)
    op.create_table("character_bibles", sa.Column("id", sa.String(36), primary_key=True), common_fk("character_bibles"),
        sa.Column("character_id", sa.String(120), nullable=False), sa.Column("semantic_key", sa.String(160), nullable=False), sa.Column("display_name", sa.String(240), nullable=False),
        sa.Column("role", sa.Text(), nullable=False), sa.Column("age_band", sa.String(120), nullable=False), sa.Column("gender_presentation", sa.String(120)),
        *[sa.Column(c, sa.Text(), nullable=False) for c in ("body_proportion_style","face_description","hairstyle","wardrobe","footwear","accessories","primary_palette","secondary_palette","expression_range","pose_guidance","cultural_notes","forbidden_variations")],
        sa.Column("reference_asset_ids", sa.Text(), nullable=False), sa.Column("review_status", sa.String(16), nullable=False), sa.Column("provenance", sa.Text(), nullable=False))
    op.create_table("environment_bibles", sa.Column("id", sa.String(36), primary_key=True), common_fk("environment_bibles"),
        *[sa.Column(c, sa.String(120 if c in ("environment_id","regional_profile_id","terrain","season") else 240), nullable=False) for c in ("environment_id","canonical_name","regional_profile_id","terrain","season","weather")],
        *[sa.Column(c, sa.Text(), nullable=False) for c in ("architecture_guidance","vegetation_guidance","water_features","road_path_guidance","time_of_day_options","lighting","visual_palette","cultural_notes","required_features","forbidden_features","provenance","reference_asset_ids")],
        sa.Column("grounding_status", sa.String(16), nullable=False), sa.Column("review_status", sa.String(16), nullable=False))
    op.create_table("scene_visual_bindings", sa.Column("id", sa.String(36), primary_key=True), common_fk("scene_visual_bindings"),
        *[sa.Column(c, sa.String(120), nullable=False) for c in ("scene_id","location_id","regional_profile_id")], sa.Column("character_ids", sa.Text(), nullable=False),
        sa.Column("character_bible_version", sa.Integer(), nullable=False), sa.Column("environment_bible_version", sa.Integer(), nullable=False),
        sa.Column("visual_style_profile_id", sa.String(120)), sa.Column("cultural_profile_id", sa.String(120)), sa.Column("grounding_status", sa.String(16), nullable=False),
        sa.Column("source_plan_hash", sa.String(64), nullable=False), sa.Column("binding_hash", sa.String(64), nullable=False))
    op.create_table("visual_prompt_packages", sa.Column("id", sa.String(36), primary_key=True), common_fk("visual_prompt_packages"),
        *[sa.Column(c, sa.Text(), nullable=False) for c in ("scene_id","positive_prompt","negative_prompt","character_tokens","environment_tokens","composition","camera_framing","lighting","color_palette","required_cultural_features","forbidden_features")],
        sa.Column("base_model_id", sa.String(160)), sa.Column("base_model_hash", sa.String(128)), sa.Column("intended_style_lora_ids", sa.Text(), nullable=False), sa.Column("seed_placeholder", sa.String(80), nullable=False),
        sa.Column("package_version", sa.String(40), nullable=False), sa.Column("package_hash", sa.String(64), nullable=False), sa.Column("governance_status", sa.String(16), nullable=False), sa.Column("release_eligible", sa.Boolean(), nullable=False), sa.Column("keyframe_status", sa.String(32), nullable=False), sa.Column("valid", sa.Boolean(), nullable=False))
    op.create_table("grounding_requirements", sa.Column("id", sa.String(36), primary_key=True), common_fk("grounding_requirements"),
        *[sa.Column(c, sa.String(32 if c == "scope_type" else 120), nullable=False) for c in ("scope_type","scope_id")], sa.Column("claim", sa.Text(), nullable=False), sa.Column("status", sa.String(16), nullable=False), sa.Column("source_reference_ids", sa.Text(), nullable=False), sa.Column("review_required", sa.Boolean(), nullable=False))

def downgrade() -> None:
    for table in ("grounding_requirements","visual_prompt_packages","scene_visual_bindings","environment_bibles","character_bibles","visual_bible_sets"):
        op.drop_table(table)
