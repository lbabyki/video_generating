"""Add controlled LoRA manifest records.

Revision ID: 0005_controlled_lora_manifests
Revises: 0004_model_registry
"""
from alembic import op
import sqlalchemy as sa
revision = "0005_controlled_lora_manifests"; down_revision = "0004_model_registry"; branch_labels = depends_on = None
def upgrade() -> None:
    op.create_table("controlled_lora_manifests", sa.Column("id", sa.String(120), primary_key=True), sa.Column("version", sa.String(64), nullable=False), sa.Column("sha256", sa.String(64), nullable=False), sa.Column("filename", sa.String(255), nullable=False), sa.Column("review_status", sa.String(32), nullable=False), sa.Column("manifest_json", sa.Text(), nullable=False))
def downgrade() -> None: op.drop_table("controlled_lora_manifests")
