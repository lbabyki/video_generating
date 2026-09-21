"""Versioned built-in ComfyUI API workflows used by technical spikes."""

from __future__ import annotations

import hashlib
import json
from typing import Any


BASELINE_PROMPT = (
    "Vietnamese educational 2D illustration for grade 4 students, "
    "the Red River Delta countryside, a calm river, green rice fields, "
    "bamboo and traditional rural houses in the distance, "
    "bright friendly colors, clear composition, daytime, "
    "no text, no watermark"
)
BASELINE_NEGATIVE_PROMPT = (
    "text, watermark, logo, signature, distorted landscape, "
    "deformed objects, photorealistic, dark horror atmosphere, "
    "political symbol"
)
BASELINE_WORKFLOW_VERSION = "phase1b-sdxl-base-v1"
BASELINE_SEED = 20260921
_ALLOWED_NODES = {
    "CheckpointLoaderSimple",
    "CLIPTextEncode",
    "EmptyLatentImage",
    "KSampler",
    "VAEDecode",
    "SaveImage",
}


def build_sdxl_baseline(checkpoint_name: str) -> dict[str, dict[str, Any]]:
    workflow: dict[str, dict[str, Any]] = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint_name}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": BASELINE_PROMPT, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": BASELINE_NEGATIVE_PROMPT, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1344, "height": 768, "batch_size": 1}},
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": BASELINE_SEED,
                "steps": 25,
                "cfg": 6.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
            },
        },
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "phase1b/sdxl-baseline"}},
    }
    validate_baseline_workflow(workflow)
    return workflow


def validate_baseline_workflow(workflow: dict[str, dict[str, Any]]) -> None:
    types = {node.get("class_type") for node in workflow.values()}
    if types - _ALLOWED_NODES or any("lora" in str(node).lower() or "custom" in str(node).lower() for node in workflow.values()):
        raise ValueError("baseline workflow must use only approved built-in nodes and no LoRA")
    if types != _ALLOWED_NODES:
        raise ValueError("baseline workflow is incomplete")
    sampler = next(node for node in workflow.values() if node["class_type"] == "KSampler")["inputs"]
    if sampler["seed"] != BASELINE_SEED or sampler["steps"] != 25 or sampler["cfg"] != 6.5:
        raise ValueError("baseline sampler parameters are not reproducible")


def workflow_sha256(workflow: dict[str, dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(workflow, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
