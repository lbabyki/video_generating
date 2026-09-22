"""Add planner execution status and local model provenance.

Revision ID: 0008_qwen_planner_provenance
Revises: 0007_prompt_compilations
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_qwen_planner_provenance"
down_revision = "0007_prompt_compilations"
branch_labels = depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("prompt_compilations") as batch:
        batch.alter_column("plan_json", existing_type=sa.Text(), nullable=True)
        batch.add_column(sa.Column("compilation_status", sa.String(32), nullable=False, server_default="SUCCEEDED"))
        batch.add_column(sa.Column("planner_provider", sa.String(32), nullable=False, server_default="mock"))
        batch.add_column(sa.Column("planner_model", sa.String(160), nullable=True))
        batch.add_column(sa.Column("resolved_model_digest", sa.String(128), nullable=True))
        batch.add_column(sa.Column("prompt_template_version", sa.String(80), nullable=False, server_default="mock-template-v1"))
        batch.add_column(sa.Column("repair_attempts", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("validation_errors_json", sa.Text(), nullable=False, server_default="[]"))
        batch.add_column(sa.Column("resource_metrics_json", sa.Text(), nullable=False, server_default="{}"))
    op.create_table(
        "prompt_model_provenance",
        sa.Column("resolved_model_digest", sa.String(128), primary_key=True),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("ollama_version", sa.String(32), nullable=True),
        sa.Column("requested_tag", sa.String(160), nullable=False),
        sa.Column("quantization", sa.String(64), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("architecture", sa.String(120), nullable=True),
        sa.Column("parameter_size", sa.String(80), nullable=True),
        sa.Column("license", sa.String(80), nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prompt_template_version", sa.String(80), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("prompt_model_provenance")
    with op.batch_alter_table("prompt_compilations") as batch:
        batch.drop_column("resource_metrics_json")
        batch.drop_column("validation_errors_json")
        batch.drop_column("repair_attempts")
        batch.drop_column("prompt_template_version")
        batch.drop_column("resolved_model_digest")
        batch.drop_column("planner_model")
        batch.drop_column("planner_provider")
        batch.drop_column("compilation_status")
        batch.alter_column("plan_json", existing_type=sa.Text(), nullable=False)
