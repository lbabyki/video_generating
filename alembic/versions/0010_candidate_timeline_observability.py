"""Add candidate validation and deterministic timeline provenance.

Revision ID: 0010_candidate_timeline_observability
Revises: 0009_qwen_run_metrics
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_candidate_timeline_observability"
down_revision = "0009_qwen_run_metrics"
branch_labels = depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("prompt_compilations") as batch:
        batch.add_column(sa.Column("validation_stage", sa.String(80), nullable=True))
        batch.add_column(sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("failed_scene_orders_json", sa.Text(), nullable=False, server_default="[]"))
        batch.add_column(sa.Column("candidate_response_sha256", sa.String(64), nullable=True))
        batch.add_column(sa.Column("candidate_diagnostic_path", sa.Text(), nullable=True))
        batch.add_column(sa.Column("timeline_provenance_json", sa.Text(), nullable=False, server_default="{}"))


def downgrade() -> None:
    with op.batch_alter_table("prompt_compilations") as batch:
        batch.drop_column("timeline_provenance_json")
        batch.drop_column("candidate_diagnostic_path")
        batch.drop_column("candidate_response_sha256")
        batch.drop_column("failed_scene_orders_json")
        batch.drop_column("error_count")
        batch.drop_column("validation_stage")
