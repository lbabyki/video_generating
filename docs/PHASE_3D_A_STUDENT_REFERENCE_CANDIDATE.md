# Phase 3D-A — Student Reference Candidate

Status: `STUDENT_REFERENCE_CANDIDATE_READY_FOR_HUMAN_REVIEW`

## Preflight

- VisualBibleSet `9f2272dd-2237-53ed-a3aa-fd570e89a75e`: `APPROVED`.
- Recurring student CharacterBible v2: `APPROVED`.
- Cultural review: `APPROVED_WITH_RESTRICTED_SCOPE`.
- ComfyUI was healthy and published only on `127.0.0.1:8188`; it was stopped after the job.
- Ollama had no loaded model; no LoRA trainer or GPU worker occupied the GPU.
- No LoRA, ControlNet, IP-Adapter, custom node, video, audio, TTS or subtitle workflow was used.

## Model and workflow

- Model: `sdxl-base-1.0`, SDXL_BASE.
- Revision: `462165984030d82259a11f4367a4eed129e94a7b`.
- Checkpoint: `sd_xl_base_1.0.safetensors`.
- SHA-256: `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`.
- Workflow: `phase3d-student-reference-v1`.
- Workflow SHA-256: `49a1c41882407fff3ab69db7691c4621ae2e9154fd77d49f76f1b62748e7f11d`.
- ComfyUI revision: `b0f4b7b294ce482a2e071d9d762c133d38c7aa07`.
- Nodes: CheckpointLoaderSimple → CLIPTextEncode → EmptyLatentImage → KSampler → VAEDecode → SaveImage.

## Prompts and parameters

The positive and negative prompts are stored in the candidate record and sidecar. They contain no UUID, governance token, database token or hash.

- Seed: `31415926`
- Sampler/scheduler: `euler` / `normal`
- Steps: `30`
- CFG: `6.0`
- Size: `1024×1024`, batch size `1`
- LoRA status: `NOT_ASSIGNED`

## Output

- Candidate ID: `8c96c167-8f2f-58b0-863e-6f8a111cd5cc`
- Relative path: `output/phase3d/student-reference/candidate-001/student-reference_00001_.png`
- SHA-256: `b703cbc64a5194be5d9a6b3106700f6af731761223f489b3047d9cb238a35493`
- Pillow verification: PNG, `1024×1024`, RGB.
- Exactly one output image was produced; no existing output was overwritten.
- Inference latency: `5114 ms`.
- VRAM before/peak/after: `1189 MiB / 8536 MiB / 1210 MiB`.

## Governance

- `governance_status=DRAFT`
- `human_review_status=PENDING`
- `reference_status=CANDIDATE`
- `release_eligible=false`
- This is not `REFERENCE_APPROVED`, `CHARACTER_CONSISTENCY_PASS`, `LORA_PASS`, `KEYFRAME_PASS`, `VISUAL_BIBLE_RENDER_LOCKED` or `PROMPT_TO_VIDEO_PASS`.
- CharacterBible, VisualBibleSet, EnvironmentBible, v1–v4 packages, ProjectPlan and compilation provenance were not changed.

## Verification

- Full pytest: 133 passed.
- Alembic current/upgrade: `0018_character_reference_candidates (head)`; FK check clean; Compose config and git diff check passed.
- No commit or push.
