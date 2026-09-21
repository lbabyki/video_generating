# Educational Video Studio

Local-first foundation for an educational-video pipeline. Phase 0A GPU recovery
is blocked; this repository does not install, launch, or simulate ComfyUI,
SDXL, LoRA inference, CUDA PyTorch, or model downloads.

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

ComfyUI is deliberately disabled behind the Compose `gpu` profile. It remains
blocked until NVIDIA, CUDA PyTorch, and (if applicable) Docker GPU checks pass.
