"""Structured semantic prompt sections for visual prompt QA."""
from alembic import op
import sqlalchemy as sa

revision = "0016_structured_prompt_packages"
down_revision = "0015_grounding_resolutions_prompt_versions"
branch_labels = depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("visual_prompt_packages") as b:
        for name, default in (("style_prompt", ""), ("environment_prompt", ""), ("subject_prompts", "[]"), ("action_prompt", ""), ("continuity_constraints", "[]"), ("workflow_metadata", "{}")):
            b.add_column(sa.Column(name, sa.Text(), nullable=False, server_default=default))

def downgrade() -> None:
    with op.batch_alter_table("visual_prompt_packages") as b:
        for name in ("workflow_metadata", "continuity_constraints", "action_prompt", "subject_prompts", "environment_prompt", "style_prompt"):
            b.drop_column(name)
