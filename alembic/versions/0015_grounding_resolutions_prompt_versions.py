"""Restricted grounding resolutions and immutable prompt package versions."""
from alembic import op
import sqlalchemy as sa

revision = "0015_grounding_resolutions_prompt_versions"
down_revision = "0014_grounding_requirement_followup"
branch_labels = depends_on = None

def upgrade() -> None:
    op.create_table(
        "grounding_resolutions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("bible_set_id", sa.String(36), sa.ForeignKey("visual_bible_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requirement_id", sa.String(36), sa.ForeignKey("grounding_requirements.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("original_requirement", sa.Text(), nullable=False),
        sa.Column("factual_evidence_status", sa.String(32), nullable=False),
        sa.Column("project_design_evidence", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("supported_scope", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("excluded_claims", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("resolution_mode", sa.String(48), nullable=False),
        sa.Column("reviewer_id", sa.String(120), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    with op.batch_alter_table("visual_prompt_packages") as b:
        b.add_column(sa.Column("package_status", sa.String(16), nullable=False, server_default="ACTIVE"))
        b.add_column(sa.Column("supported_evidence_ids", sa.Text(), nullable=False, server_default="[]"))
        b.add_column(sa.Column("project_design_source_ids", sa.Text(), nullable=False, server_default="[]"))
        b.add_column(sa.Column("excluded_claims", sa.Text(), nullable=False, server_default="[]"))

def downgrade() -> None:
    with op.batch_alter_table("visual_prompt_packages") as b:
        b.drop_column("excluded_claims")
        b.drop_column("project_design_source_ids")
        b.drop_column("supported_evidence_ids")
        b.drop_column("package_status")
    op.drop_table("grounding_resolutions")
