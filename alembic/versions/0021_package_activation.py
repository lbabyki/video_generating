"""Separate package lifecycle from runtime selection."""
from alembic import op
import sqlalchemy as sa

revision = "0021_package_activation"
down_revision = "0020_mascot_scene_mapping"
branch_labels = depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("visual_prompt_packages") as b:
        b.add_column(sa.Column("activation_status", sa.String(16), nullable=False, server_default="CANDIDATE"))
        b.add_column(sa.Column("runtime_selectable", sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade() -> None:
    with op.batch_alter_table("visual_prompt_packages") as b:
        b.drop_column("runtime_selectable")
        b.drop_column("activation_status")
