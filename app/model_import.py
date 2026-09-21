"""Explicit, resumable, local checkpoint import with no startup side effects."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app.domain.model import ModelManifest, validate_download


MIN_FREE_BYTES = 25 * 1024**3


def _safe_target(root: Path, filename: str) -> Path:
    target = (root / filename).resolve()
    if target.parent != root.resolve():
        raise ValueError("model filename escapes checkpoint directory")
    return target


def _headers() -> dict[str, str]:
    token = os.environ.get("HF_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


def ensure_disk_space(destination: Path) -> None:
    if shutil.disk_usage(destination).free < MIN_FREE_BYTES:
        raise RuntimeError("at least 25 GiB of free disk space is required before model import")


def import_checkpoint(manifest: ModelManifest, checkpoints_dir: Path, *, timeout: int = 60) -> Path:
    """Download only after explicit invocation, validate, then atomically publish."""
    manifest.validate()
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    ensure_disk_space(checkpoints_dir)
    target = _safe_target(checkpoints_dir, manifest.local_filename)
    if target.exists():
        validate_download(target, manifest)
        return target

    staging_dir = checkpoints_dir / ".staging"
    staging_dir.mkdir(exist_ok=True)
    partial = _safe_target(staging_dir, f"{manifest.local_filename}.part")
    offset = partial.stat().st_size if partial.exists() else 0
    if offset == manifest.file_size:
        try:
            validate_download(partial, manifest)
            os.replace(partial, target)
            return target
        except ValueError:
            offset = 0
    if offset >= manifest.file_size:
        # A stale or malformed partial must never be resumed or treated as a model.
        offset = 0
    url = f"https://huggingface.co/{manifest.source_repository}/resolve/{manifest.source_revision}/{manifest.source_filename}"
    headers = _headers()
    if offset:
        headers["Range"] = f"bytes={offset}-"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            content_range = response.headers.get("Content-Range", "")
            append = offset > 0 and response.status == 206 and content_range.startswith(f"bytes {offset}-")
            with partial.open("ab" if append else "wb") as stream:
                while chunk := response.read(1024 * 1024):
                    stream.write(chunk)
                stream.flush()
                os.fsync(stream.fileno())
    except HTTPError as exc:
        if exc.code in {401, 403}:
            raise PermissionError("Hugging Face authorization or license acceptance is required; accept terms and set HF_TOKEN before retrying") from exc
        raise
    try:
        validate_download(partial, manifest)
        os.replace(partial, target)
    except Exception:
        # Preserve the partial file for a resumable retry; it is never a workflow input.
        raise
    return target


def write_import_metadata(manifest: ModelManifest, target: Path) -> Path:
    metadata = target.with_suffix(target.suffix + ".manifest.json")
    temporary = metadata.with_suffix(metadata.suffix + ".tmp")
    temporary.write_text(json.dumps(manifest.with_imported_at().as_dict(), indent=2, sort_keys=True) + "\n")
    os.replace(temporary, metadata)
    return metadata
