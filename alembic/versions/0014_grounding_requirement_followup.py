"""Track requirements that remain partially supported.

Revision ID: 0014_grounding_requirement_followup
Revises: 0013_human_reviewers
"""
from alembic import op
import sqlalchemy as sa

revision = "0014_grounding_requirement_followup"
down_revision = "0013_human_reviewers"
branch_labels = depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("grounding_requirements") as b:
        b.add_column(sa.Column("needs_more_evidence", sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade() -> None:
    with op.batch_alter_table("grounding_requirements") as b:
        b.drop_column("needs_more_evidence")
