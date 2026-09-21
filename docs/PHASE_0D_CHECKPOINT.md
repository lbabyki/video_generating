# Phase 0D checkpoint — Vietnamese Cultural and Content Governance

## Status

- Phase 0A GPU recovery: **BLOCKED**.
- Phase 0B foundation scaffold: **COMPLETED**.
- Phase 0C runtime/integration: **COMPLETED WITH WARNINGS**.
- Phase 0D cultural/content governance: **COMPLETED WITH WARNINGS**.
- Phase 1 ComfyUI/SDXL/LoRA inference: **BLOCKED**.
- Overall Phase 0 is **PARTIALLY_BLOCKED**, not PASS.

## Files changed

- Cultural documents: `docs/cultural/*.md`, including eight Lesson 08 golden prompt records.
- Runtime: `docker-compose.yml` adds profile-gated `frontend-check`.
- Governance: `app/governance/service.py`, `app/api/governance.py`, `app/api/main.py`.
- Persistence: `app/db/models.py` and migration `0003_cultural_governance.py`.
- Tests: `tests/test_cultural_governance.py`, `tests/test_governance_api.py`.

## Migration and API

Migration `0003_cultural_governance` creates versioned cultural profiles, reference source provenance, dataset-asset review, and scene-governance tables.

- `GET /governance/cultural-profiles/{name}`
- `POST /governance/scenes/{scene_id}/reviews`
- `POST /governance/scenes/{scene_id}/reviews/approve`
- `POST /governance/scenes/{scene_id}/reviews/reject`
- `POST /governance/scenes/{scene_id}/approve`
- `POST /governance/scenes/{scene_id}/lock`
- `POST /governance/scenes/{scene_id}/release-render`

Only a `LOCKED` scene with both content and cultural reviews approved is release eligible. Prompt, LoRA, weight, seed, keyframe, reference, or cultural-profile changes must invalidate approval and return the scene to `DRAFT`.

## Tests actually run

```bash
.venv/bin/python -m pytest -q
.venv/bin/alembic upgrade head
.venv/bin/alembic current
sg docker -c 'docker compose run --rm frontend-check'
```

| Check | Result | Classification |
|---|---|---|
| Python tests | **PASS** — 21 passed, 0 failed | TESTED |
| Cultural transitions, invalidation, immutable profile | **PASS** | TESTED |
| Release block without cultural review | **PASS** | TESTED |
| Dataset license and reference provenance rejection | **PASS** | TESTED |
| Migration | **PASS** — `0003_cultural_governance (head)` | TESTED |
| Node host runtime | **WARN** — `v26.7.0`, unchanged and not production target | TESTED |
| Project frontend runtime | **PASS** — `node:24-bookworm` ran `v24.21.0` with read-only mount | TESTED |
| ComfyUI client contract | **PASS** | MOCK-TESTED only |
| ComfyUI/SDXL/LoRA/GPU rendering | **BLOCKED** | NOT TESTED |

## GPU blocker

No PyTorch CUDA, SDXL, LoRA, ComfyUI, NVIDIA driver/CUDA/kernel modification, or GPU inference was performed. `nvidia-smi` remains the Phase 1 blocker. GPU metadata appears in `/proc/driver/nvidia/gpus`; device nodes remain absent in this session. Only an administrator may assess `nvidia-modprobe` after driver recovery; this project did not run it.

## Governance statement

Hệ thống áp dụng hồ sơ phong cách Việt Nam và quy trình kiểm duyệt bắt buộc trước khi phát hành.

This workflow reduces avoidable errors; it does not guarantee absolute cultural correctness. Human review remains required.

## Proposed commit

`feat(phase0d): add Vietnamese cultural governance and node24 verification`
