"""Local human reviewer identity bootstrap and role authorization."""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import HumanReviewer, HumanReviewerAudit

ROLES = {"PROJECT_OWNER", "CULTURAL_REVIEWER", "CONTENT_REVIEWER", "LEGAL_REVIEWER"}
STATUSES = {"ACTIVE", "INACTIVE", "REVOKED"}
ROLE_RULES = {
    "evidence": {"PROJECT_OWNER", "CULTURAL_REVIEWER", "CONTENT_REVIEWER"},
    "character": {"PROJECT_OWNER", "CONTENT_REVIEWER"},
    "environment": {"PROJECT_OWNER", "CULTURAL_REVIEWER", "CONTENT_REVIEWER"},
    "cultural": {"CULTURAL_REVIEWER"},
    "project_design": {"PROJECT_OWNER"},
}

def normalize_display_name(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value or "").strip()).casefold()

def bootstrap_reviewer(db: Session, display_name: str, role: str, *, method: str = "local_cli") -> HumanReviewer:
    name = " ".join((display_name or "").split())
    if not name: raise ValueError("display name must not be empty")
    role = (role or "").strip().upper()
    if role not in ROLES: raise ValueError("invalid reviewer role")
    existing = db.scalar(select(HumanReviewer).where(HumanReviewer.role == role).where(HumanReviewer.display_name.is_not(None)))
    for candidate in db.scalars(select(HumanReviewer).where(HumanReviewer.role == role)):
        if normalize_display_name(candidate.display_name) == normalize_display_name(name): return candidate
    reviewer = HumanReviewer(id=str(uuid4()), display_name=name, role=role, status="ACTIVE", provenance=json.dumps({"method": method, "normalized_display_name": normalize_display_name(name)}), created_by_method=method)
    db.add(reviewer); db.flush()
    db.add(HumanReviewerAudit(id=str(uuid4()), reviewer_id=reviewer.id, action="REVIEWER_BOOTSTRAPPED", details_json=json.dumps({"role": role, "method": method}, ensure_ascii=False)))
    db.commit(); db.refresh(reviewer); return reviewer

def require_reviewer(db: Session, reviewer_id: str, purpose: str) -> HumanReviewer:
    reviewer = db.get(HumanReviewer, reviewer_id)
    if reviewer is None: raise ValueError("reviewer does not exist")
    if reviewer.status != "ACTIVE": raise ValueError("reviewer is not ACTIVE")
    if purpose not in ROLE_RULES or reviewer.role not in ROLE_RULES[purpose]: raise ValueError("reviewer role is not authorized for this decision")
    return reviewer
