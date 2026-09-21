#!/usr/bin/env python3
"""Explicit Phase 1B SDXL checkpoint import; this is never a startup action."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.db.session import SessionLocal
from app.domain.model import ModelManifest
from app.model_import import import_checkpoint, write_import_metadata
from app.model_registry import register_import


ROOT = Path(__file__).parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifests/sdxl-base-1.0.json")
    parser.add_argument("--checkpoints-dir", type=Path, default=ROOT / "models/checkpoints")
    parser.add_argument("--confirm-import", action="store_true", help="required explicit acknowledgement before downloading")
    arguments = parser.parse_args()
    if not arguments.confirm_import:
        parser.error("refusing download without --confirm-import")
    manifest = ModelManifest.from_dict(json.loads(arguments.manifest.read_text()))
    target = import_checkpoint(manifest, arguments.checkpoints_dir)
    metadata = write_import_metadata(manifest, target)
    with SessionLocal() as session:
        register_import(session, manifest)
    print(f"IMPORTED {target.name} ({target.stat().st_size} bytes); metadata={metadata.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
