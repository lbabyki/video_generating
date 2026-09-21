"""Dataset governance records. Revision ID: 0006_dataset_governance. Revises: 0005_controlled_lora_manifests."""
from alembic import op
import sqlalchemy as sa
revision="0006_dataset_governance"; down_revision="0005_controlled_lora_manifests"; branch_labels=depends_on=None
def upgrade():
 op.create_table("dataset_versions",sa.Column("id",sa.String(120),primary_key=True),sa.Column("version",sa.Integer,nullable=False),sa.Column("kind",sa.String(32),nullable=False),sa.Column("state",sa.String(32),nullable=False)); op.create_table("dataset_assets",sa.Column("id",sa.String(120),primary_key=True),sa.Column("dataset_id",sa.String(120),nullable=False),sa.Column("sha256",sa.String(64),nullable=False),sa.Column("perceptual_hash",sa.String(64),nullable=False),sa.Column("review_status",sa.String(32),nullable=False),sa.Column("audit",sa.Text,nullable=False))
def downgrade(): op.drop_table("dataset_assets"); op.drop_table("dataset_versions")
