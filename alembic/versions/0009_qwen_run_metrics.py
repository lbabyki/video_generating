"""Persist planner seed, latency, and deterministic validation result.

Revision ID: 0009_qwen_run_metrics
Revises: 0008_qwen_planner_provenance
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_qwen_run_metrics"
down_revision = "0008_qwen_planner_provenance"
branch_labels = depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("prompt_compilations") as batch:
        batch.add_column(sa.Column("planner_seed", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("planner_temperature", sa.Float(), nullable=True))
        batch.add_column(sa.Column("latency_ms", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("validation_result_json", sa.Text(), nullable=False, server_default="{}"))


def downgrade() -> None:
    with op.batch_alter_table("prompt_compilations") as batch:
        batch.drop_column("validation_result_json")
        batch.drop_column("latency_ms")
        batch.drop_column("planner_temperature")
        batch.drop_column("planner_seed")
