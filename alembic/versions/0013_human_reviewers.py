"""Add local human reviewer identities.

Revision ID: 0013_human_reviewers
Revises: 0012_grounding_review
"""
from alembic import op
import sqlalchemy as sa

revision = "0013_human_reviewers"
down_revision = "0012_grounding_review"
branch_labels = depends_on = None

def upgrade() -> None:
    op.create_table("human_reviewers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True)),
        sa.Column("provenance", sa.Text(), nullable=False),
        sa.Column("created_by_method", sa.String(40), nullable=False),
        sa.UniqueConstraint("display_name", "role", name="uq_human_reviewer_name_role"))
    op.create_table("human_reviewer_audits",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("human_reviewers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

def downgrade() -> None:
    op.drop_table("human_reviewer_audits")
    op.drop_table("human_reviewers")
