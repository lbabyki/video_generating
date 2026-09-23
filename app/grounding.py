from __future__ import annotations

import hashlib
import json
import mimetypes
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid4, uuid5

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (CharacterBible, EvidenceLink, EnvironmentBible, GroundingRequirement,
    ReferenceSource, VisualBibleAudit, VisualBibleReview, VisualBibleSet, VisualPromptPackage)

REFERENCE_ROOT = Path("/home/ailab/videoAI_project/videoAI_data/references").resolve()
MAX_REFERENCE_BYTES = int(os.getenv("GROUNDING_MAX_REFERENCE_BYTES", str(50 * 1024 * 1024)))
SOURCE_TYPES = {"FACTUAL_REFERENCE", "CULTURAL_REFERENCE", "VISUAL_REFERENCE", "TRAINING_ASSET"}
PERMISSIONS = {"REFERENCE_ONLY", "TRAINING_ALLOWED", "REQUIRES_LEGAL_REVIEW", "UNKNOWN", "BLOCKED"}
REVIEW_STATUSES = {"PENDING", "SUPPORTED", "PARTIALLY_SUPPORTED", "REJECTED", "BLOCKED"}
MAGIC = {".pdf": (b"%PDF-", "application/pdf"), ".png": (b"\x89PNG\r\n\x1a\n", "image/png"), ".jpg": (b"\xff\xd8\xff", "image/jpeg"), ".jpeg": (b"\xff\xd8\xff", "image/jpeg"), ".webp": (b"RIFF", "image/webp")}

def training_allowed(source: ReferenceSource) -> bool:
    return source.usage_permission == "TRAINING_ALLOWED"

def _audit(db, bible, action, actor=None, details=None):
    db.add(VisualBibleAudit(id=str(uuid4()), bible_set_id=bible.id, action=action, actor_id=actor, details_json=json.dumps(details or {}, ensure_ascii=False)))

def _invalidate(db, bible, action, actor=None):
    if bible.status == "LOCKED": raise ValueError("LOCKED bible sets are immutable")
    if bible.status in {"APPROVED", "IN_REVIEW"}: bible.status = "DRAFT"
    for package in db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id == bible.id)): package.valid = False
    _audit(db, bible, action, actor)

def register_local(db: Session, payload: dict) -> ReferenceSource:
    rel = payload.get("local_relative_path")
    if not rel or Path(rel).is_absolute(): raise ValueError("local_relative_path must be relative")
    candidate = (REFERENCE_ROOT / Path(rel)).resolve()
    try: candidate.relative_to(REFERENCE_ROOT)
    except ValueError as exc: raise ValueError("path escapes reference root") from exc
    if not candidate.is_file() or candidate.is_symlink(): raise ValueError("reference file must be a regular file under the reference root")
    if candidate.stat().st_size > MAX_REFERENCE_BYTES: raise ValueError("reference file exceeds configured size limit")
    ext = candidate.suffix.casefold()
    if ext not in MAGIC: raise ValueError("unsupported reference extension")
    magic, mime = MAGIC[ext]
    with candidate.open("rb") as f: head=f.read(16); digest=hashlib.sha256(f.read() if False else candidate.read_bytes()).hexdigest()
    if not head.startswith(magic): raise ValueError("file MIME signature does not match extension")
    declared = payload.get("mime_type")
    if declared and declared != mime: raise ValueError("declared MIME does not match file")
    existing = db.scalar(select(ReferenceSource).where(ReferenceSource.sha256 == digest))
    if existing: return existing
    source_id = str(uuid5(NAMESPACE_URL, f"reference:{digest}"))
    source = ReferenceSource(id=source_id, title=payload.get("title", candidate.name), source_url=payload.get("canonical_url") or f"local:{rel}", provenance=json.dumps({"relative_path": rel, "registered": True}), license=payload.get("license", "UNKNOWN"), organization=payload.get("organization"), source_type=payload.get("source_type", "FACTUAL_REFERENCE"), local_file_path=rel, canonical_url=payload.get("canonical_url"), publication_date=payload.get("publication_date"), access_date=payload.get("access_date") or datetime.now(UTC).date().isoformat(), page_or_section=payload.get("page_or_section"), sha256=digest, mime_type=mime, usage_permission=payload.get("usage_permission", "UNKNOWN"), attribution=payload.get("attribution"), notes=payload.get("notes"), review_status="PENDING")
    if source.source_type not in SOURCE_TYPES or source.usage_permission not in PERMISSIONS: raise ValueError("invalid source category or usage permission")
    db.add(source); db.commit(); db.refresh(source); return source

def add_evidence(db: Session, requirement_id: str, payload: dict) -> EvidenceLink:
    requirement = db.get(GroundingRequirement, requirement_id)
    source = db.get(ReferenceSource, payload.get("source_id"))
    if not requirement or not source: raise ValueError("requirement or source not found")
    page = (payload.get("page_or_section") or "").strip()
    summary = (payload.get("evidence_summary") or "").strip()
    if not page: raise ValueError("page_or_section is required")
    if not summary or len(summary) > 1200: raise ValueError("evidence_summary must be a short paraphrase")
    bible = db.get(VisualBibleSet, requirement.bible_set_id)
    if bible.status == "LOCKED": raise ValueError("LOCKED bible sets are immutable")
    link = EvidenceLink(id=str(uuid4()), grounding_requirement_id=requirement_id, source_id=source.id, page_or_section=page, evidence_summary=summary, supported_claim=payload.get("supported_claim", requirement.claim), notes=payload.get("notes"), review_status="PENDING")
    db.add(link); _invalidate(db,bible,"EVIDENCE_ADDED"); db.commit(); db.refresh(link); return link

def review_evidence(db: Session, evidence_id: str, payload: dict) -> EvidenceLink:
    link=db.get(EvidenceLink,evidence_id); source=db.get(ReferenceSource,link.source_id) if link else None
    if not link or not source: raise ValueError("evidence not found")
    status=payload.get("review_status")
    if status not in REVIEW_STATUSES or not payload.get("reviewer_id"): raise ValueError("human reviewer and valid review status are required")
    req=db.get(GroundingRequirement,link.grounding_requirement_id); bible=db.get(VisualBibleSet,req.bible_set_id)
    if bible.status == "LOCKED": raise ValueError("LOCKED bible sets are immutable")
    link.review_status=status; link.reviewer_id=payload["reviewer_id"]; link.reviewed_at=datetime.now(UTC); link.notes=payload.get("notes")
    links=db.scalars(select(EvidenceLink).where(EvidenceLink.grounding_requirement_id==req.id)).all()
    if status == "SUPPORTED" and source.usage_permission != "BLOCKED" and any(x.review_status=="SUPPORTED" for x in links): req.status="SUPPORTED"; req.review_required=False
    elif status in {"REJECTED","BLOCKED"}: req.status=status; req.review_required=True
    _invalidate(db,bible,"EVIDENCE_REVIEWED",payload["reviewer_id"]); db.commit(); db.refresh(link); return link

def save_review(db: Session, bible_id: str, target_type: str, target_id: str, payload: dict) -> VisualBibleReview:
    bible=db.get(VisualBibleSet,bible_id)
    if not bible: raise ValueError("bible not found")
    if bible.status == "LOCKED": raise ValueError("LOCKED bible sets are immutable")
    if payload.get("status") != "APPROVED" or not payload.get("reviewer_id"): raise ValueError("human APPROVED review is required")
    review=VisualBibleReview(id=str(uuid4()),bible_set_id=bible_id,target_type=target_type,target_id=target_id,checklist_json=json.dumps(payload.get("checklist",{}),ensure_ascii=False),status="APPROVED",reviewer_id=payload["reviewer_id"],reviewed_at=datetime.now(UTC),notes=payload.get("notes"))
    db.add(review)
    if target_type == "CHARACTER":
        item = db.get(CharacterBible, target_id)
        if item and item.bible_set_id == bible_id: item.review_status = "APPROVED"
    if target_type == "ENVIRONMENT":
        item = db.get(EnvironmentBible, target_id)
        if item and item.bible_set_id == bible_id: item.review_status = "APPROVED"
    _invalidate(db,bible,f"{target_type}_REVIEWED",payload["reviewer_id"]); db.commit(); db.refresh(review); return review

def grounding_view(db: Session, bible_id: str) -> dict:
    bible=db.get(VisualBibleSet,bible_id)
    if not bible: raise ValueError("bible not found")
    reqs=db.scalars(select(GroundingRequirement).where(GroundingRequirement.bible_set_id==bible_id)).all()
    evid=[]
    for req in reqs: evid.extend(db.scalars(select(EvidenceLink).where(EvidenceLink.grounding_requirement_id==req.id)).all())
    return {"bible_set_id":bible_id,"requirements":[{"id":r.id,"claim":r.claim,"status":r.status,"review_required":r.review_required} for r in reqs],"evidence":[{"id":e.id,"grounding_requirement_id":e.grounding_requirement_id,"source_id":e.source_id,"page_or_section":e.page_or_section,"evidence_summary":e.evidence_summary,"review_status":e.review_status,"reviewer_id":e.reviewer_id} for e in evid]}
