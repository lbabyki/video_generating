"""Create Phase 0B registry tables.

Revision ID: 0001_foundation
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lora_registry",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("base_model", sa.String(length=120), nullable=False),
        sa.Column("revision", sa.String(length=160), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("license", sa.String(length=160), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("name", name="uq_lora_name"), sa.UniqueConstraint("sha256", name="uq_lora_sha256"),
    )
    op.create_table(
        "visual_style_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("prompt_prefix", sa.Text(), nullable=False),
        sa.Column("negative_prompt", sa.Text(), nullable=False),
        sa.Column("aspect_ratio", sa.String(length=16), nullable=False),
        sa.Column("lora_id", sa.String(length=36), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("name", name="uq_profile_name"),
    )


def downgrade() -> None:
    op.drop_table("visual_style_profiles")
    op.drop_table("lora_registry")
