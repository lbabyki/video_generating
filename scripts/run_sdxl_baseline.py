#!/usr/bin/env python3
"""Submit exactly one approved Phase 1B baseline workflow to local ComfyUI."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import time
from pathlib import Path

from app.comfyui_client import ComfyArtifact, ComfyUIClient
from app.db.session import SessionLocal
from app.domain.model import ModelManifest, sha256_file, validate_download
from app.model_registry import require_approved
from app.workflows import (
    BASELINE_NEGATIVE_PROMPT,
    BASELINE_PROMPT,
    BASELINE_SEED,
    BASELINE_WORKFLOW_VERSION,
    build_sdxl_baseline,
    workflow_sha256,
)


ROOT = Path(__file__).parents[1]


def nvidia_smi_snapshot() -> str:
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader"],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


async def run(arguments: argparse.Namespace) -> Path:
    manifest = ModelManifest.from_dict(json.loads(arguments.manifest.read_text()))
    model_path = ROOT / "models/checkpoints" / manifest.local_filename
    validate_download(model_path, manifest)
    with SessionLocal() as session:
        require_approved(session, manifest.id, manifest.sha256)

    workflow = build_sdxl_baseline(manifest.local_filename)
    workflow_hash = workflow_sha256(workflow)
    output_dir = ROOT / "output/phase1b"
    if output_dir.exists() and list(output_dir.glob("sdxl-baseline*.png")):
        raise RuntimeError("a Phase 1B baseline output already exists; refusing to submit another inference")
    before_vram = nvidia_smi_snapshot()
    observed_vram = [before_vram]
    started = time.monotonic()
    async with ComfyUIClient(arguments.comfyui_url) as client:
        prompt_id = await client.submit(workflow, "phase1b-sdxl-baseline")
        history: dict[str, object] = {}
        for _ in range(arguments.timeout_seconds):
            history = await client.history(prompt_id)
            if prompt_id in history:
                break
            observed_vram.append(nvidia_smi_snapshot())
            await asyncio.sleep(1)
        else:
            raise TimeoutError("ComfyUI baseline job did not complete before timeout")
        record = history[prompt_id]
        outputs = record.get("outputs", {})  # type: ignore[union-attr]
        image = outputs["7"]["images"][0]
        artifact = ComfyArtifact(image["filename"], image.get("subfolder", ""), image.get("type", "output"))
        content = await client.artifact(artifact)
    elapsed_seconds = time.monotonic() - started
    after_vram = nvidia_smi_snapshot()
    output = ROOT / "output" / artifact.subfolder / artifact.filename
    if not output.is_file() or output.read_bytes() != content:
        raise RuntimeError("ComfyUI artifact API output does not match local output bind mount")
    metadata = {
        "model_id": manifest.id,
        "model_sha256": manifest.sha256,
        "model_revision": manifest.source_revision,
        "comfyui_revision": (ROOT / "docker/comfyui/COMFYUI_REVISION").read_text().strip(),
        "workflow_version": BASELINE_WORKFLOW_VERSION,
        "workflow_sha256": workflow_hash,
        "prompt": BASELINE_PROMPT,
        "negative_prompt": BASELINE_NEGATIVE_PROMPT,
        "seed": BASELINE_SEED,
        "sampler": "euler",
        "scheduler": "normal",
        "steps": 25,
        "cfg": 6.5,
        "width": 1344,
        "height": 768,
        "inference_seconds": round(elapsed_seconds, 3),
        "vram_before": before_vram,
        "vram_observed_during": observed_vram,
        "vram_after": after_vram,
        "output_sha256": sha256_file(output),
        "governance_status": "DRAFT",
    }
    sidecar = output.with_suffix(output.suffix + ".metadata.json")
    sidecar.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), **metadata}, sort_keys=True))
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifests/sdxl-base-1.0.json")
    parser.add_argument("--comfyui-url", default="http://127.0.0.1:8188")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    arguments = parser.parse_args()
    asyncio.run(run(arguments))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
