# Phase 1A — ComfyUI GPU Runtime checkpoint

Status: **PASS WITH WARNING** (server-runtime acceptance criteria passed).

This checkpoint validates a local-only ComfyUI server and its CUDA visibility.
It does **not** start Phase 1B: no checkpoint, SDXL, LoRA, custom node, or
inference workflow was installed or run.

## Changed files

- `.gitignore` — ignores runtime model, media, and ComfyUI user-state content;
  only `.gitkeep` files are retained where needed.
- `docker-compose.yml` — local `comfyui` image in the `gpu` profile, GPU
  reservation, localhost-only port binding, eight explicit runtime bind mounts,
  and `/system_stats` healthcheck.
- `docker/comfyui/Dockerfile` — non-root Python 3.12 ComfyUI image.
- `docker/comfyui/COMFYUI_REVISION` — official source revision record.
- `docker/comfyui/requirements.lock` — exact Python dependency resolution used
  by the built image, including PyTorch CUDA 12.8 wheels.
- `models/{checkpoints,loras,vae,controlnet,clip_vision}/.gitkeep`,
  `input/.gitkeep`, `output/.gitkeep`, `user/.gitkeep` — empty bind-mount
  directory markers.
- `scripts/comfyui_smoke.py` — real local server smoke test.
- `tests/test_comfyui_runtime_config.py` — static Compose/Dockerfile safeguards.
- `README.md` — Phase 1A setup and scope.

## Pinned runtime

| Component | Pin / observed runtime |
| --- | --- |
| ComfyUI source | `b0f4b7b294ce482a2e071d9d762c133d38c7aa07` from `https://github.com/comfyanonymous/ComfyUI.git` |
| ComfyUI reported version | `0.37.0` |
| Base image | `nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04@sha256:ac55d124da4882b497f732d8dfd9a702d5447a5f29d08d56da6f64f0a1eb34bc` |
| Container Python | `3.12.3` |
| PyTorch | `2.11.0+cu128` |
| torchvision / torchaudio | `0.26.0+cu128` / `2.11.0+cu128` |
| CUDA reported by torch | `12.8` |
| Container user | `comfyui` (non-root) |

## Commands and actual results

| Command | Result |
| --- | --- |
| `docker compose config --quiet` | PASS |
| `.venv/bin/python -m pytest -q` | PASS — `23 passed in 0.24s` |
| `sg docker -c 'docker compose --profile gpu build comfyui'` | PASS — locally built `local/educational-video-comfyui:1a-b0f4b7b` |
| `sg docker -c 'docker compose --profile gpu up -d --force-recreate comfyui'` | PASS |
| `sg docker -c '.venv/bin/python scripts/comfyui_smoke.py'` | PASS — healthy, localhost-only, CUDA/NVIDIA visible |
| `sg docker -c 'docker compose --profile gpu ps comfyui'` | PASS — `Up ... (healthy)`, `127.0.0.1:8188->8188/tcp` |
| `docker compose --profile gpu exec -T comfyui python ...` | PASS — Python 3.12.3, CUDA available, `NVIDIA GeForce RTX 5090` |
| `nvidia-smi --query-gpu=...` while service was running | PASS — RTX 5090, driver `580.167.08`, `32607 MiB` total, `1700 MiB` used (server-idle baseline) |
| `docker compose --profile gpu logs --tail=100 comfyui` | PASS — server started; no `CUDA OOM` text |

`GET http://127.0.0.1:8188/system_stats` returned HTTP 200 during the smoke
test. Docker inspection in that test rejects any port mapping other than one
host mapping on `127.0.0.1`, so the API was not published to a public address.

## Safety and scope checks

- The service uses `gpus: all`, is not privileged, has `no-new-privileges`, and
  does not mount `/var/run/docker.sock`.
- No model or LoRA was downloaded. The five model mount directories contain
  only `.gitkeep`; there was no image generation or simulated inference.
- No third-party custom node was installed. The upstream ComfyUI checkout logs
  its bundled `websocket_image_save.py`, which is not an added custom node.
- ComfyUI created its own SQLite user-state files under the ignored `user/`
  runtime bind mount. They are not model assets and are not tracked by Git.

## Warning and resolved build issue

The upstream unpinned `torchaudio` dependency initially resolved to a CUDA 13
binary and server startup failed with `libcudart.so.13: cannot open shared
object file`. `docker/comfyui/requirements.lock` now pins the official
`torchaudio==2.11.0+cu128` wheel together with the verified Python dependency
set, and the final lockfile-built runtime smoke test passed. ComfyUI logs a
non-blocking recommendation for CUDA 13 optimized operations; CUDA 12.8
successfully initialised the requested RTX 5090 runtime and this phase
intentionally keeps the specified PyTorch CUDA 12.8 pin.

## Remaining work / blocker

Phase 1A is complete. Model acquisition, manifest approval, SDXL + `.safetensors`
LoRA loading, workflow submission, and all inference remain intentionally out
of scope for this checkpoint and must be performed only in the next approved
phase. No NVIDIA driver, host CUDA, kernel component, `nvidia-modprobe`, or
Docker daemon setting was changed.

Suggested commit message:

```text
feat(comfyui): add pinned local GPU runtime and health smoke test
```
