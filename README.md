# Educational Video Studio

Local-first foundation for an educational-video pipeline. Phase 1A provides a
local-only ComfyUI GPU server runtime; it does not install models, LoRAs,
custom nodes, or perform inference.

## Runtime

The project uses user-managed **Python 3.12** in `.venv`. System Python 3.14
is not a ComfyUI runtime.

```bash
~/.local/bin/uv sync --extra dev
.venv/bin/python -m pytest -q
```

Production Node is pinned to **24.x** in `.nvmrc` and `package.json`. The host
Node 26 must not be used for a production build. When a Node version manager is
installed, activate Node 24 and verify it with `node --version` in this folder.

## Local services

Valkey binds to `127.0.0.1:6379` only. If group membership has not propagated,
use a fresh login shell or `newgrp docker`; never chmod the Docker socket.

```bash
sg docker -c 'docker compose up -d valkey'
.venv/bin/python scripts/rq_smoke.py
```

## ComfyUI GPU runtime (Phase 1A)

ComfyUI is isolated behind the Compose `gpu` profile and only publishes
`127.0.0.1:8188`. Its Docker image is built locally from the pinned official
ComfyUI revision recorded in `docker/comfyui/COMFYUI_REVISION`; it never
downloads a checkpoint or LoRA. Runtime model and media directories are
Git-ignored bind mounts.

```bash
sg docker -c 'docker compose --profile gpu build comfyui'
sg docker -c 'docker compose --profile gpu up -d comfyui'
sg docker -c '.venv/bin/python scripts/comfyui_smoke.py'
```

The Phase 1A smoke test verifies container health, the local-only
`/system_stats` API, a CUDA/NVIDIA device response, and no CUDA OOM in the
last 100 log lines. It is a server-runtime check only; SDXL/LoRA installation
and image generation remain a later phase.
