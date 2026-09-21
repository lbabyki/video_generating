"""Add cultural profiles, source provenance, assets, and scene governance.

Revision ID: 0003_cultural_governance
Revises: 0002_versioned_style_profiles
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_cultural_governance"
down_revision = "0002_versioned_style_profiles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("cultural_profiles", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("state", sa.String(16), nullable=False), sa.Column("guidance", sa.Text(), nullable=False), sa.UniqueConstraint("name", "version", name="uq_cultural_profile_version"))
    op.create_table("reference_sources", sa.Column("id", sa.String(36), primary_key=True), sa.Column("title", sa.String(240), nullable=False), sa.Column("source_url", sa.Text(), nullable=False), sa.Column("provenance", sa.Text(), nullable=False), sa.Column("license", sa.String(240), nullable=False))
    op.create_table("dataset_asset_reviews", sa.Column("id", sa.String(36), primary_key=True), sa.Column("source_id", sa.String(36), sa.ForeignKey("reference_sources.id"), nullable=False), sa.Column("asset_name", sa.String(240), nullable=False), sa.Column("intended_use", sa.String(120), nullable=False), sa.Column("decision", sa.String(16), nullable=False))
    op.create_table("scene_governance", sa.Column("id", sa.String(36), primary_key=True), sa.Column("state", sa.String(32), nullable=False), sa.Column("content_review", sa.String(16), nullable=False), sa.Column("cultural_review", sa.String(16), nullable=False), sa.Column("cultural_profile_id", sa.String(36), sa.ForeignKey("cultural_profiles.id"), nullable=True))


def downgrade() -> None:
    op.drop_table("scene_governance")
    op.drop_table("dataset_asset_reviews")
    op.drop_table("reference_sources")
    op.drop_table("cultural_profiles")
