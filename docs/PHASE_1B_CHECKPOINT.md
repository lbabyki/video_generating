# Phase 1B — SDXL Base baseline checkpoint

Status: **PASS WITH WARNING**. One controlled SDXL Base 1.0 technical baseline
was imported and rendered through the local ComfyUI HTTP API. It is `DRAFT`
for governance and is not approved for content, cultural review, or release.

## Model provenance and license review

| Field | Value |
| --- | --- |
| Source | `stabilityai/stable-diffusion-xl-base-1.0` |
| Pinned revision | `462165984030d82259a11f4367a4eed129e94a7b` |
| Source file / local file | `sd_xl_base_1.0.safetensors` |
| Format / architecture | `SAFETENSORS` / `SDXL_BASE` |
| Size / SHA-256 | `6,938,078,334` bytes / `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b` |
| License | `openrail++`, [CreativeML Open RAIL++-M](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/462165984030d82259a11f4367a4eed129e94a7b/LICENSE.md) |
| License review | `REVIEWED_RESTRICTED`; commercial use is `REQUIRES_LEGAL_REVIEW` |
| Registry review | `APPROVED` for this technical inference only |

The model API reported `gated: false`; no HF token was required or recorded.
The importer only reads `HF_TOKEN` from the environment when needed and never
logs or persists it. It checks 25 GiB free space, downloads into ignored
staging, supports verified range resume, validates byte count/SHA-256 and the
safetensors header, then atomically renames the model into `models/checkpoints`.

## Workflow and output

- Workflow version/hash: `phase1b-sdxl-base-v1` /
  `3609b0e2777b2e7415868eba596d9bdf104ef4a0aa58d815f2500092b7eb31b3`.
- Nodes: built-in `CheckpointLoaderSimple`, two `CLIPTextEncode`,
  `EmptyLatentImage`, `KSampler`, `VAEDecode`, and `SaveImage` only.
- Fixed seed `20260921`; 1344×768; batch 1; 25 steps; CFG 6.5; `euler` /
  `normal` (verified supported by the pinned ComfyUI API).
- Prompt and negative prompt are stored in ignored output sidecar metadata.
- Output: `output/phase1b/sdxl-baseline_00001_.png`; SHA-256
  `ab0dd786fd51c4f05510124e08c9275d4d68a02a00c774e7e2522ea27798c076`.
- Pillow verification in the container: `PNG`, `(1344, 768)`, verified.
- Client wall time: `5.138s`; ComfyUI reported `4.84s` execution.
- VRAM observed: 1332 MiB before, peak observed 8461 MiB during, 8171 MiB
  after (RTX 5090, 32607 MiB total).

No LoRA, ControlNet, IP-Adapter, video inference, or third-party custom node
was used. Exactly one baseline render was submitted; the runner refuses a
second output with the same Phase 1B prefix.

## Changes

- Migration `0004_model_registry` and shared checkpoint registry model.
- Strict SDXL checkpoint manifest, explicit importer, provenance persistence,
  and traversal/partial-download safeguards.
- Versioned built-in ComfyUI API workflow and real baseline runner.
- Tests for extensions, pinned source revision, SHA mismatch, license metadata,
  approval gate, forbidden nodes, reproducibility, traversal, partial handling,
  and Git-ignore rules.

## Actual verification

| Command / check | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q` | PASS — `32 passed` |
| `ALEMBIC_DATABASE_URL=... alembic upgrade head` | PASS — clean DB at `0004_model_registry (head)` |
| `.venv/bin/alembic upgrade head` | PASS |
| `docker compose config --quiet` | PASS |
| `scripts/comfyui_smoke.py` | PASS |
| `scripts/import_sdxl_model.py --confirm-import` | PASS — source hash/size/safetensors validation and atomic publish |
| `scripts/run_sdxl_baseline.py` | PASS — one API workflow, history/artifact verified |
| `nvidia-smi` before/during/after | PASS — values recorded above |
| Pillow PNG validation | PASS |

## Warnings

ComfyUI logs retain its upstream CUDA 13 optimization recommendation, while
the verified pinned CUDA 12.8 runtime operated successfully. The model license
contains use restrictions; this checkpoint makes no automatic commercial-use
determination. The produced image remains governance `DRAFT` and requires the
existing content/cultural review process before any release.

Suggested commit message:

```text
feat(phase1b): add controlled SDXL baseline import and render
```
