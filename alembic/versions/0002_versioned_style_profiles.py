"""Add registry lifecycle and ordered versioned style profiles.

Revision ID: 0002_versioned_style_profiles
Revises: 0001_foundation
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_versioned_style_profiles"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("lora_registry") as batch:
        batch.add_column(sa.Column("state", sa.String(length=16), nullable=False, server_default="DRAFT"))
    with op.batch_alter_table("visual_style_profiles") as batch:
        batch.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
        batch.add_column(sa.Column("state", sa.String(length=16), nullable=False, server_default="DRAFT"))
        batch.drop_constraint("uq_profile_name", type_="unique")
        batch.create_unique_constraint("uq_profile_name_version", ["name", "version"])
    op.create_table(
        "visual_style_profile_loras",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("profile_id", sa.String(length=36), sa.ForeignKey("visual_style_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lora_id", sa.String(length=36), sa.ForeignKey("lora_registry.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("model_strength", sa.Float(), nullable=False),
        sa.Column("clip_strength", sa.Float(), nullable=False),
        sa.UniqueConstraint("profile_id", "position", name="uq_profile_lora_position"),
    )


def downgrade() -> None:
    op.drop_table("visual_style_profile_loras")
    with op.batch_alter_table("visual_style_profiles") as batch:
        batch.drop_constraint("uq_profile_name_version", type_="unique")
        batch.create_unique_constraint("uq_profile_name", ["name"])
        batch.drop_column("state")
        batch.drop_column("version")
    with op.batch_alter_table("lora_registry") as batch:
        batch.drop_column("state")
