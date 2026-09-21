# Phase 0 Status

## Overall: PARTIALLY_BLOCKED

### Phase 0A — NVIDIA/GPU recovery: BLOCKED

`nvidia-smi`/NVML is failing. No NVIDIA driver, CUDA Toolkit, kernel module,
or PyTorch CUDA installation is authorized while it fails. ComfyUI is disabled
behind the Docker `gpu` profile and must not be started.

### Phase 0B — foundation scaffold: COMPLETED

- Project runtime pins: Python 3.12 only and Node.js 24 LTS only.
- FastAPI, SQLite/SQLAlchemy/Alembic, Valkey/RQ and local storage are scaffolded.
- LoRA registry requires source, revision, SHA-256, license, and `.safetensors`
  filename before later enablement.
- The FFmpeg spike is CPU-only. It does not claim GPU, model, or LoRA inference.

### Phase 0C — Runtime and Integration Foundation: COMPLETED WITH GPU BLOCKERS

Python 3.12 is user-managed in `.venv`, dependencies are locked in `uv.lock`,
and CPU/mock integration tests are complete. Phase 1 remains BLOCKED.

### Phase 0D — Vietnamese Cultural and Content Governance: COMPLETED WITH WARNINGS

Node 24 was verified only in the `node:24-bookworm` tooling container; the host
Node 26 remains unchanged. Cultural governance is enforced by versioned
profiles, provenance checks, mandatory review states, and release locking.

## Docker session

The account is listed in the `docker` group, but the current session does not
have that effective group. Start a fresh login session or run `newgrp docker`,
then rerun `python3 scripts/preflight.py --docker-gpu`. Do not use `chmod 666`
on the Docker socket.
