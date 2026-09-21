# Phase 0C checkpoint — Runtime and Integration Foundation

## State

- Phase 0A — NVIDIA/GPU recovery: **BLOCKED**.
- Phase 0B — foundation scaffold: **COMPLETED**.
- Phase 0C — runtime and integration foundation: **COMPLETED WITH WARNINGS**.
- Phase 1 — ComfyUI/SDXL/LoRA inference: **BLOCKED**.
- Overall Phase 0: **PARTIALLY_BLOCKED**; it is not PASS.

## TESTED

| Area | Result | Evidence |
|---|---|---|
| Python runtime | PASS | `.venv/bin/python --version` is Python 3.12.13, managed by user-scoped uv; system Python 3.14 was untouched. |
| Dependencies | PASS | `uv.lock` was generated; pinned dependencies were installed into `.venv`. |
| Python tests | PASS | `14 passed in 0.22s` with Python 3.12.13. |
| SQLite migrations | PASS | Clean database upgraded to `0002_versioned_style_profiles (head)`. |
| SQLite FK | PASS | Connection returns `PRAGMA foreign_keys = 1`. |
| FastAPI health | PASS | A temporary localhost-only Uvicorn process returned `{"status":"ok","comfyui_enabled":false}` and was stopped. |
| Docker | PASS | `sg docker -c 'docker info …'` reports daemon 29.7.2; Compose validates. |
| Valkey/RQ | PASS | Pinned Valkey 8.0.2 runs only on `127.0.0.1:6379`; a real RQ job was enqueued, consumed, consumed by a fresh worker, and returned an idempotent duplicate result. |
| FFmpeg worker module | PASS | CPU-only tests cover ffprobe validation, path traversal, partial output, and idempotent existing output. |

## MOCK-TESTED

- `ComfyUIClient` submit, history/progress, cancel and artifact contracts were
  exercised using `httpx.MockTransport`. No ComfyUI server, model, GPU, or
  inference request was used.

## NOT TESTED / BLOCKED

- Real ComfyUI, SDXL, LoRA, CUDA PyTorch, VRAM, image generation and GPU Docker
  smoke are blocked by Phase 0A.
- `nvidia-smi`/NVML remains FAIL. `/proc/driver/nvidia/gpus/0000:01:00.0`
  identifies RTX 5090 with firmware/driver 580.167.08 and Device Minor 0, but
  `/dev/nvidia*` remains absent in this session. An administrator may assess
  `nvidia-modprobe` after driver recovery; this project made no such call.
- Node.js 24 is **not tested**: no Node version manager was present and the host
  remains Node 26.7.0. `.nvmrc` and `package.json` pin 24.x for production.

## Migrations

- `0001_foundation`: initial LoRA Registry and Visual Style Profile tables.
- `0002_versioned_style_profiles`: LoRA lifecycle state; profile version/state;
  ordered profile-LoRA bindings with distinct `model_strength` and `clip_strength`.

Approved profiles are revised into a new DRAFT version in domain logic; ordered
LoRA lists and strength ranges are validated by unit tests.

## Commands actually run

```bash
~/.local/bin/uv python install 3.12
~/.local/bin/uv venv --python 3.12 .venv
~/.local/bin/uv lock
~/.local/bin/uv sync --extra dev
.venv/bin/python -m pytest -q
.venv/bin/alembic upgrade head
.venv/bin/alembic current
.venv/bin/python scripts/rq_smoke.py
sg docker -c 'docker info --format {{.ServerVersion}}'
sg docker -c 'docker compose config --quiet'
```

## Docker session guidance

The account is listed in the `docker` group but the original session does not
have its effective membership. Use a fresh login session or `newgrp docker`.
For an isolated command, `sg docker -c '<command>'` works. Do not use `chmod
666 /var/run/docker.sock`.

## Phase 1 gate

Do not start Phase 1 until all applicable gates pass: `nvidia-smi`,
`torch.cuda.is_available() == true`, and Docker GPU smoke if ComfyUI will run
in Docker.
