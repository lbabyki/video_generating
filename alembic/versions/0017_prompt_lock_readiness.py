"""Model provenance, cohorts, and static keyframe fields for V4 review."""
from alembic import op
import sqlalchemy as sa

revision = "0017_prompt_lock_readiness"
down_revision = "0016_structured_prompt_packages"
branch_labels = depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("visual_prompt_packages") as b:
        cols = [
            ("base_model_revision", sa.String(80), None), ("base_model_sha256", sa.String(64), None),
            ("checkpoint_filename", sa.String(255), None), ("model_architecture", sa.String(80), None),
            ("style_lora_ids", sa.Text(), "[]"), ("character_lora_ids", sa.Text(), "[]"),
            ("lora_status", sa.String(24), "NOT_ASSIGNED"), ("background_cohorts", sa.Text(), "{}"),
            ("keyframe_prompt", sa.Text(), ""), ("keyframe_hash", sa.String(64), None),
            ("motion_intent", sa.Text(), ""), ("intended_camera_motion", sa.Text(), ""),
            ("video_transition_hint", sa.Text(), ""),
        ]
        for name, typ, default in cols:
            kw = {"nullable": True} if default is None else {"nullable": False, "server_default": default}
            b.add_column(sa.Column(name, typ, **kw))

def downgrade() -> None:
    with op.batch_alter_table("visual_prompt_packages") as b:
        for name in ("video_transition_hint", "intended_camera_motion", "motion_intent", "keyframe_hash", "keyframe_prompt", "background_cohorts", "lora_status", "character_lora_ids", "style_lora_ids", "model_architecture", "checkpoint_filename", "base_model_sha256", "base_model_revision"):
            b.drop_column(name)
