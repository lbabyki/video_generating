"""Persist deterministic mascot scene bindings and overlay metadata."""
from alembic import op
import sqlalchemy as sa

revision = "0020_mascot_scene_mapping"
down_revision = "0019_mascot_assets"
branch_labels = depends_on = None

def upgrade() -> None:
    op.create_table("mascot_scene_bindings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("bible_set_id", sa.String(36), sa.ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scene_id", sa.String(120), nullable=False),
        sa.Column("mascot_bible_id", sa.String(36), sa.ForeignKey("mascot_character_bibles.id"), nullable=False),
        sa.Column("asset_id", sa.String(36), sa.ForeignKey("mascot_assets.id"), nullable=False),
        sa.Column("expression", sa.String(80), nullable=False), sa.Column("role", sa.String(80), nullable=False),
        sa.Column("preferred_anchor", sa.String(32), nullable=False), sa.Column("max_frame_height_ratio", sa.Float(), nullable=False, server_default="0.22"),
        sa.Column("subtitle_safe_bottom_ratio", sa.Float(), nullable=False, server_default="0.18"), sa.Column("entrance", sa.String(80), nullable=False),
        sa.Column("exit", sa.String(80), nullable=False), sa.Column("motion_hint", sa.String(120), nullable=False),
        sa.Column("alpha_required", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("mirror_allowed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("prop_bearing", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("inset_only", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    with op.batch_alter_table("visual_prompt_packages") as b:
        b.add_column(sa.Column("mascot_overlay", sa.Text(), nullable=False, server_default="{}"))

def downgrade() -> None:
    with op.batch_alter_table("visual_prompt_packages") as b:
        b.drop_column("mascot_overlay")
    op.drop_table("mascot_scene_bindings")
