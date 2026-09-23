"""Persist human review state for overlay smoke diagnostics."""
from alembic import op
import sqlalchemy as sa

revision = "0023_overlay_review_fields"
down_revision = "0022_overlay_render_attempts"
branch_labels = depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("overlay_render_attempts") as b:
        b.add_column(sa.Column("static_visual_review", sa.String(24), nullable=False, server_default="PENDING"))
        b.add_column(sa.Column("motion_visual_review", sa.String(24), nullable=False, server_default="PENDING"))
        b.add_column(sa.Column("overlay_smoke_status", sa.String(24), nullable=False, server_default="PENDING"))
        b.add_column(sa.Column("reviewer_id", sa.String(36), nullable=True))
        b.add_column(sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
        b.add_column(sa.Column("review_notes", sa.Text(), nullable=False, server_default=""))

def downgrade() -> None:
    with op.batch_alter_table("overlay_render_attempts") as b:
        for name in ("review_notes", "reviewed_at", "reviewer_id", "overlay_smoke_status", "motion_visual_review", "static_visual_review"):
            b.drop_column(name)
