"""Persist deterministic prompt compilation plans.

Revision ID: 0007_prompt_compilations
Revises: 0006_dataset_governance
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_prompt_compilations"
down_revision = "0006_dataset_governance"
branch_labels = depends_on = None


def upgrade() -> None:
    op.create_table(
        "prompt_compilations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("raw_prompt", sa.Text(), nullable=False),
        sa.Column("normalized_request_json", sa.Text(), nullable=False),
        sa.Column("planner_type", sa.String(120), nullable=False),
        sa.Column("planner_version", sa.String(32), nullable=False),
        sa.Column("schema_version", sa.String(16), nullable=False),
        sa.Column("cultural_profile_version", sa.String(32), nullable=False),
        sa.Column("plan_json", sa.Text(), nullable=False),
        sa.Column("validation_warnings_json", sa.Text(), nullable=False),
        sa.Column("governance_state", sa.String(32), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("request_hash", name="uq_prompt_compilations_request_hash"),
    )


def downgrade() -> None:
    op.drop_table("prompt_compilations")
