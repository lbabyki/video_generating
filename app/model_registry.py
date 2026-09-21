"""Persistence adapter for the shared model registry."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import ModelRegistryEntry
from app.domain.model import ModelManifest


def register_import(session: Session, manifest: ModelManifest) -> ModelRegistryEntry:
    if not manifest.is_approved():
        raise ValueError("only APPROVED models may be registered for inference")
    existing = session.get(ModelRegistryEntry, manifest.id)
    if existing is not None and existing.sha256 != manifest.sha256:
        raise ValueError("model id already exists with a different SHA-256")
    values = manifest.with_imported_at().as_dict()
    values["imported_at"] = datetime.fromisoformat(values["imported_at"])
    if existing is None:
        entry = ModelRegistryEntry(**values)
        session.add(entry)
    else:
        for field, value in values.items():
            setattr(existing, field, value)
        entry = existing
    session.commit()
    return entry


def require_approved(session: Session, model_id: str, sha256: str) -> ModelRegistryEntry:
    entry = session.get(ModelRegistryEntry, model_id)
    if entry is None or entry.review_status != "APPROVED" or entry.sha256 != sha256:
        raise ValueError("model is not approved for inference")
    return entry
