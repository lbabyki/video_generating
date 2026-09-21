"""Approved checkpoint manifest rules for local-only inference."""

from __future__ import annotations

import hashlib
import json
import re
import struct
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_HF_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_MAX_SAFETENSORS_HEADER = 100 * 1024 * 1024


@dataclass(frozen=True)
class ModelManifest:
    id: str
    name: str
    model_type: str
    architecture: str
    source_repository: str
    source_revision: str
    source_filename: str
    local_filename: str
    sha256: str
    file_size: int
    format: str
    compatible_workflow: str
    license_id: str
    license_url: str
    license_review_status: str
    commercial_use: str
    review_status: str
    imported_at: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ModelManifest":
        required = tuple(cls.__dataclass_fields__)
        missing = [field for field in required if field != "imported_at" and not payload.get(field)]
        if missing:
            raise ValueError(f"model manifest missing required fields: {', '.join(missing)}")
        manifest = cls(**{field: payload.get(field) for field in required})
        manifest.validate()
        return manifest

    def validate(self) -> None:
        if self.model_type != "CHECKPOINT" or self.architecture != "SDXL_BASE":
            raise ValueError("only SDXL_BASE CHECKPOINT manifests are supported in Phase 1B")
        if self.format != "SAFETENSORS" or not self.source_filename.endswith(".safetensors") or not self.local_filename.endswith(".safetensors"):
            raise ValueError("checkpoint weights must use the .safetensors format")
        if Path(self.source_filename).name != self.source_filename or Path(self.local_filename).name != self.local_filename:
            raise ValueError("checkpoint filenames must not contain paths")
        if not _HF_COMMIT.fullmatch(self.source_revision):
            raise ValueError("source_revision must be a pinned 40-character Hugging Face commit SHA")
        if not _SHA256.fullmatch(self.sha256):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        if self.file_size <= 0:
            raise ValueError("file_size must be positive")
        if not all((self.id, self.name, self.source_repository, self.compatible_workflow, self.license_id, self.license_url, self.license_review_status, self.commercial_use, self.review_status)):
            raise ValueError("model manifest provenance and license fields are required")

    def with_imported_at(self) -> "ModelManifest":
        return replace(self, imported_at=datetime.now(UTC).isoformat())

    def is_approved(self) -> bool:
        return self.review_status == "APPROVED"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_safetensors(path: Path) -> None:
    """Validate the non-pickle safetensors header without loading model weights."""
    if not (path.name.endswith(".safetensors") or path.name.endswith(".safetensors.part")):
        raise ValueError("checkpoint weights must use the .safetensors format")
    with path.open("rb") as stream:
        header_size_bytes = stream.read(8)
        if len(header_size_bytes) != 8:
            raise ValueError("invalid safetensors header")
        header_size = struct.unpack("<Q", header_size_bytes)[0]
        if header_size <= 0 or header_size > _MAX_SAFETENSORS_HEADER or header_size > path.stat().st_size - 8:
            raise ValueError("invalid safetensors header length")
        try:
            header = json.loads(stream.read(header_size))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid safetensors JSON header") from exc
    if not isinstance(header, dict) or not any(key != "__metadata__" for key in header):
        raise ValueError("safetensors header has no tensor entries")


def validate_download(path: Path, manifest: ModelManifest) -> None:
    manifest.validate()
    if path.stat().st_size != manifest.file_size:
        raise ValueError("downloaded file size does not match manifest")
    if sha256_file(path) != manifest.sha256:
        raise ValueError("downloaded file SHA-256 does not match manifest")
    validate_safetensors(path)
