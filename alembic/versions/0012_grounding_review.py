"""Add source evidence and visual bible review records.

Revision ID: 0012_grounding_review
Revises: 0011_visual_bibles
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_grounding_review"
down_revision = "0011_visual_bibles"
branch_labels = depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("reference_sources") as b:
        for name, typ in [("organization",sa.String(240)),("source_type",sa.String(32)),("local_file_path",sa.Text()),("canonical_url",sa.Text()),("publication_date",sa.String(40)),("access_date",sa.String(40)),("page_or_section",sa.String(240)),("sha256",sa.String(64)),("mime_type",sa.String(80)),("usage_permission",sa.String(32)),("attribution",sa.Text()),("notes",sa.Text()),("review_status",sa.String(16))]:
            b.add_column(sa.Column(name,typ,nullable=True))
    op.create_table("evidence_links", sa.Column("id",sa.String(36),primary_key=True), sa.Column("grounding_requirement_id",sa.String(36),sa.ForeignKey("grounding_requirements.id",ondelete="CASCADE"),nullable=False), sa.Column("source_id",sa.String(36),sa.ForeignKey("reference_sources.id"),nullable=False), sa.Column("page_or_section",sa.String(240),nullable=False), sa.Column("evidence_summary",sa.Text(),nullable=False), sa.Column("supported_claim",sa.Text(),nullable=False), sa.Column("reviewer_id",sa.String(120)), sa.Column("review_status",sa.String(24),nullable=False), sa.Column("reviewed_at",sa.DateTime(timezone=True)), sa.Column("notes",sa.Text()))
    op.create_table("visual_bible_reviews", sa.Column("id",sa.String(36),primary_key=True), sa.Column("bible_set_id",sa.String(36),sa.ForeignKey("visual_bible_sets.id",ondelete="CASCADE"),nullable=False), sa.Column("target_type",sa.String(24),nullable=False), sa.Column("target_id",sa.String(120),nullable=False), sa.Column("checklist_json",sa.Text(),nullable=False), sa.Column("status",sa.String(24),nullable=False), sa.Column("reviewer_id",sa.String(120)), sa.Column("reviewed_at",sa.DateTime(timezone=True)), sa.Column("notes",sa.Text()))
    op.create_table("visual_bible_audits", sa.Column("id",sa.String(36),primary_key=True), sa.Column("bible_set_id",sa.String(36),sa.ForeignKey("visual_bible_sets.id",ondelete="CASCADE"),nullable=False), sa.Column("action",sa.String(80),nullable=False), sa.Column("actor_id",sa.String(120)), sa.Column("details_json",sa.Text(),nullable=False), sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))

def downgrade() -> None:
    for t in ("visual_bible_audits","visual_bible_reviews","evidence_links"): op.drop_table(t)
    with op.batch_alter_table("reference_sources") as b:
        for name in ("review_status","notes","attribution","usage_permission","mime_type","sha256","page_or_section","access_date","publication_date","canonical_url","local_file_path","source_type","organization"): b.drop_column(name)
