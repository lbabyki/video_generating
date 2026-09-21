# Phase 0 checkpoint — PARTIALLY_BLOCKED

## Completed (Phase 0B)

- Local repository scaffold with a Python 3.12-only project pin and Node 24 LTS pin.
- FastAPI health endpoint foundation; no server was started.
- SQLite/SQLAlchemy models and Alembic initial migration for LoRA Registry and
  Visual Style Profiles.
- Valkey/RQ queue factory and local-only storage provider.
- CPU-only FFmpeg LOW_RESOURCE smoke spike that creates and verifies a 640×360
  H.264 MP4. It uses no GPU, model, or LoRA inference.
- ComfyUI is profile-gated in `docker-compose.yml`; it has no runnable image
  and is not enabled by default.
- NVIDIA diagnostic evidence is in `diagnostics/`; all commands were read-only.

## Actual verification

Commands run:

```bash
python3 -m py_compile scripts/preflight.py scripts/ffmpeg_low_resource_spike.py app/storage.py app/domain/lora.py app/media/low_resource.py
python3 -m unittest discover -s tests -v
python3 scripts/ffmpeg_low_resource_spike.py
docker compose config --quiet
```

| Check | Status | Evidence |
|---|---|---|
| Unit tests | PASS | 6 tests passed, including filesystem traversal rejection, LoRA `.safetensors` policy, command limits, and CPU FFmpeg encode. |
| FFmpeg LOW_RESOURCE spike | PASS | FFmpeg generated and FFprobe verified a 640×360 H.264 MP4. |
| Python 3.12 runtime | WARN | Not installed/detectable; no venv or dependency installation was performed. |
| Node.js 24 runtime | WARN | Host has Node 26.7.0; `.nvmrc` and package engine reject it as the production target. |
| Docker Compose configuration | PASS | Configuration validates; GPU profile is omitted unless explicitly selected. |
| NVIDIA/NVML | FAIL | RTX 5090 + module 580.167.08 detected, but `nvidia-smi` fails and `/dev/nvidia*` is absent. |
| Docker GPU | WARN | Current session lacks effective Docker-group access; GPU smoke test cannot run. |

## GPU-blocked work

ComfyUI installation/runtime, CUDA PyTorch, approved SDXL/LoRA download,
keyframe rendering, inference timing/VRAM measurements, and all Phase 1 work.

## Safe next commands after the current session is refreshed

```bash
newgrp docker
python3 scripts/preflight.py --docker-gpu
```

`newgrp docker` changes the current shell's effective group only. Do not chmod
the Docker socket. Do not alter the NVIDIA driver, CUDA Toolkit, or modules.
