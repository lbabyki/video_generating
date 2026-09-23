"""Register mascot assets and provisional mascot CharacterBible."""
from alembic import op
import sqlalchemy as sa

revision = "0019_mascot_assets"
down_revision = "0018_character_reference_candidates"
branch_labels = depends_on = None

def upgrade() -> None:
    op.create_table("mascot_character_bibles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("bible_set_id", sa.String(36), sa.ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provisional_name", sa.String(80), nullable=False), sa.Column("character_type", sa.String(80), nullable=False),
        sa.Column("role", sa.String(160), nullable=False), sa.Column("runtime_presentation", sa.String(80), nullable=False),
        sa.Column("recurring", sa.Boolean(), nullable=False), sa.Column("student_identity", sa.Boolean(), nullable=False),
        sa.Column("teacher_identity", sa.Boolean(), nullable=False), sa.Column("cultural_claim", sa.String(32), nullable=False),
        sa.Column("school_uniform", sa.String(32), nullable=False), sa.Column("red_scarf", sa.String(32), nullable=False),
        sa.Column("style", sa.Text(), nullable=False), sa.Column("identity_constraints", sa.Text(), nullable=False),
        sa.Column("governance_status", sa.String(16), nullable=False, server_default="DRAFT"),
        sa.Column("release_eligible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("review_status", sa.String(24), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("mascot_assets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mascot_bible_id", sa.String(36), sa.ForeignKey("mascot_character_bibles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("canonical_filename", sa.String(160), nullable=False), sa.Column("source_relative_path", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False, unique=True), sa.Column("mime_type", sa.String(80), nullable=False),
        sa.Column("magic_valid", sa.Boolean(), nullable=False), sa.Column("width", sa.Integer(), nullable=False), sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("color_mode", sa.String(24), nullable=False), sa.Column("alpha_present", sa.Boolean(), nullable=False),
        sa.Column("expression_label", sa.String(80), nullable=False), sa.Column("props_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("prop_contamination", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("source_provenance", sa.Text(), nullable=False),
        sa.Column("creation_tool", sa.String(160), nullable=False), sa.Column("ownership_declaration", sa.Text(), nullable=False),
        sa.Column("reference_permission", sa.String(32), nullable=False), sa.Column("training_permission", sa.String(32), nullable=False),
        sa.Column("review_status", sa.String(24), nullable=False, server_default="PENDING"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

def downgrade() -> None:
    op.drop_table("mascot_assets")
    op.drop_table("mascot_character_bibles")
