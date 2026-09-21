"""Add registry entries for approved checkpoint imports.

Revision ID: 0004_model_registry
Revises: 0003_cultural_governance
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_model_registry"
down_revision = "0003_cultural_governance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_registry",
        sa.Column("id", sa.String(120), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False, unique=True, index=True),
        sa.Column("model_type", sa.String(32), nullable=False),
        sa.Column("architecture", sa.String(64), nullable=False),
        sa.Column("source_repository", sa.String(240), nullable=False),
        sa.Column("source_revision", sa.String(64), nullable=False),
        sa.Column("source_filename", sa.String(255), nullable=False),
        sa.Column("local_filename", sa.String(255), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False, unique=True),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("format", sa.String(32), nullable=False),
        sa.Column("compatible_workflow", sa.String(120), nullable=False),
        sa.Column("license_id", sa.String(120), nullable=False),
        sa.Column("license_url", sa.Text(), nullable=False),
        sa.Column("license_review_status", sa.String(32), nullable=False),
        sa.Column("commercial_use", sa.String(64), nullable=False),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("model_registry")
