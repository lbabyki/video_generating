#!/usr/bin/env python3
"""Run exactly one isolated Phase 1C cultural prompt-control experiment."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from app.comfyui_client import ComfyArtifact, ComfyUIClient
from app.db.session import SessionLocal
from app.domain.model import ModelManifest, sha256_file, validate_download
from app.model_registry import require_approved
from app.workflows import BASELINE_SEED, build_sdxl_baseline, workflow_sha256
from scripts.run_sdxl_baseline import nvidia_smi_snapshot


ROOT = Path(__file__).parents[1]
EXPERIMENT_ID = "PHASE_1C:CULTURAL_PROMPT_CONTROL:experiment-001"
VARIANT = "B_BASE_NO_LORA"
PREFIX = "phase1c/experiment-001/variant-b-base-no-lora"
PARENT_OUTPUT = ROOT / "output/phase1b/sdxl-baseline_00001_.png"
POSITIVE_PROMPT = (
    "A bright educational 2D illustration for Vietnamese grade 4 students, "
    "a flat low-lying alluvial landscape of the Red River Delta in northern Vietnam, "
    "wide green rice paddies, a calm river, a small wooden rural boat, "
    "bamboo hedges, a large banyan tree, simple northern Vietnamese village houses "
    "with red clay tile roofs, a small traditional Vietnamese communal house "
    "in the far distance, clear open composition, friendly colors, daytime, "
    "geographically accurate, culturally accurate Vietnamese countryside, "
    "no text, no logo, no watermark"
)
NEGATIVE_PROMPT = (
    "text, watermark, logo, signature, distorted landscape, deformed objects, "
    "photorealistic, dark horror atmosphere, political symbol, foreign architecture, "
    "non-Vietnamese traditional clothing, non-Vietnamese flags, inaccurate geography"
)


async def main() -> int:
    manifest = ModelManifest.from_dict(json.loads((ROOT / "manifests/sdxl-base-1.0.json").read_text()))
    validate_download(ROOT / "models/checkpoints" / manifest.local_filename, manifest)
    with SessionLocal() as session:
        require_approved(session, manifest.id, manifest.sha256)
    if not PARENT_OUTPUT.is_file():
        raise RuntimeError("Phase 1B parent output is missing")
    parent_sha256 = sha256_file(PARENT_OUTPUT)
    output_dir = ROOT / "output/phase1c/experiment-001"
    if output_dir.exists() and list(output_dir.glob("variant-b-base-no-lora*.png")):
        raise RuntimeError("Phase 1C experiment output already exists; refusing a second render")
    workflow = build_sdxl_baseline(manifest.local_filename, positive_prompt=POSITIVE_PROMPT, negative_prompt=NEGATIVE_PROMPT, filename_prefix=PREFIX)
    workflow_hash = workflow_sha256(workflow)
    before = nvidia_smi_snapshot()
    observed = [before]
    started = time.monotonic()
    async with ComfyUIClient("http://127.0.0.1:8188") as client:
        prompt_id = await client.submit(workflow, "phase1c-cultural-prompt-control")
        for _ in range(900):
            history = await client.history(prompt_id)
            if prompt_id in history:
                break
            observed.append(nvidia_smi_snapshot())
            await asyncio.sleep(1)
        else:
            raise TimeoutError("Phase 1C experiment timed out")
        image = history[prompt_id]["outputs"]["7"]["images"][0]
        artifact = ComfyArtifact(image["filename"], image.get("subfolder", ""), image.get("type", "output"))
        content = await client.artifact(artifact)
    elapsed = time.monotonic() - started
    after = nvidia_smi_snapshot()
    output = ROOT / "output" / artifact.subfolder / artifact.filename
    if not output.is_file() or output.read_bytes() != content:
        raise RuntimeError("artifact API and isolated output bind mount differ")
    metadata = {
        "phase": "PHASE_1C", "experiment": "CULTURAL_PROMPT_CONTROL", "experiment_id": EXPERIMENT_ID,
        "variant": VARIANT, "parent_phase1b_output_sha256": parent_sha256,
        "change_reason": "CULTURAL_PROMPT_CORRECTION", "model_id": manifest.id,
        "model_revision": manifest.source_revision, "model_sha256": manifest.sha256,
        "comfyui_revision": (ROOT / "docker/comfyui/COMFYUI_REVISION").read_text().strip(),
        "workflow_sha256": workflow_hash, "prompt": POSITIVE_PROMPT, "negative_prompt": NEGATIVE_PROMPT,
        "seed": BASELINE_SEED, "sampler": "euler", "scheduler": "normal", "steps": 25, "cfg": 6.5,
        "width": 1344, "height": 768, "batch_size": 1, "inference_seconds": round(elapsed, 3),
        "vram_before": before, "vram_observed_during": observed, "vram_after": after,
        "output_sha256": sha256_file(output), "governance_status": "DRAFT",
    }
    output.with_suffix(output.suffix + ".metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), **metadata}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
