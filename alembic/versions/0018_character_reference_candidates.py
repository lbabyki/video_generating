"""Persist controlled character reference candidates."""
from alembic import op
import sqlalchemy as sa

revision = "0018_character_reference_candidates"
down_revision = "0017_prompt_lock_readiness"
branch_labels = depends_on = None

def upgrade() -> None:
    op.create_table(
        "character_reference_candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("character_bible_id", sa.String(36), sa.ForeignKey("character_bibles.id"), nullable=False),
        sa.Column("character_id", sa.String(120), nullable=False),
        sa.Column("character_bible_version", sa.Integer(), nullable=False),
        sa.Column("bible_set_id", sa.String(36), sa.ForeignKey("visual_bible_sets.id"), nullable=False),
        sa.Column("bible_set_version", sa.Integer(), nullable=False),
        sa.Column("base_model_id", sa.String(160), nullable=False),
        sa.Column("base_model_revision", sa.String(80), nullable=False),
        sa.Column("base_model_sha256", sa.String(64), nullable=False),
        sa.Column("positive_prompt", sa.Text(), nullable=False),
        sa.Column("negative_prompt", sa.Text(), nullable=False),
        sa.Column("workflow_version", sa.String(80), nullable=False),
        sa.Column("workflow_sha256", sa.String(64), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("sampler", sa.String(40), nullable=False),
        sa.Column("scheduler", sa.String(40), nullable=False),
        sa.Column("steps", sa.Integer(), nullable=False),
        sa.Column("cfg", sa.Float(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("output_relative_path", sa.Text(), nullable=False),
        sa.Column("output_sha256", sa.String(64), nullable=False),
        sa.Column("comfyui_revision", sa.String(80), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("vram_before", sa.Text(), nullable=False),
        sa.Column("vram_peak", sa.Text(), nullable=False),
        sa.Column("vram_after", sa.Text(), nullable=False),
        sa.Column("governance_status", sa.String(16), nullable=False, server_default="DRAFT"),
        sa.Column("human_review_status", sa.String(24), nullable=False, server_default="PENDING"),
        sa.Column("reference_status", sa.String(24), nullable=False, server_default="CANDIDATE"),
        sa.Column("release_eligible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("lora_status", sa.String(24), nullable=False, server_default="NOT_ASSIGNED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("character_reference_candidates")
