# Phase 0 — Preflight Report

Generated: `2026-09-19T09:02:10Z`

Summary: **14 PASS / 1 WARN / 0 FAIL**.

| Check | Status | Evidence | Safe remediation |
|---|---|---|---|
| Operating system | **PASS** | Linux-7.0.0-1013-oem-x86_64-with-glibc2.43 | — |
| CPU | **PASS** | AMD Ryzen 7 9850X3D 8-Core Processor; 16 logical CPUs; 8 cores × 1 socket(s) | — |
| RAM | **PASS** | 129328996 kB | — |
| Workspace disk | **PASS** | 236.5 GiB free of 914.8 GiB at / | — |
| Storage device | **PASS** | nvme1n1 disk 0 KINGSTON SNV3S1000G 931.5G; nvme0n1 disk 0 KINGSTON SNV3S2000G   1.8T | — |
| NVIDIA GPU / driver | **PASS** | NVIDIA GeForce RTX 5090, 580.167.08, 32607 MiB | — |
| git | **PASS** | /usr/bin/git; git version 2.53.0 | — |
| docker | **PASS** | /usr/bin/docker; Docker version 29.7.2, build a7dcaa6 | — |
| python3 | **PASS** | /usr/bin/python3; Python 3.14.4 | — |
| node | **PASS** | /home/ailab/.local/bin/node; v26.7.0 | — |
| ffmpeg | **PASS** | /usr/bin/ffmpeg; ffmpeg version 8.0.1-3ubuntu2 Copyright (c) 2000-2025 the FFmpeg developers built with gcc 15 (Ubuntu 15.2.0-13ubuntu3) configuration: --prefix=/usr --extra-version=3ubuntu2 --toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu --arch=amd64 --enable-gpl --disable-stripping --dis | — |
| ffprobe | **PASS** | /usr/bin/ffprobe; ffprobe version 8.0.1-3ubuntu2 Copyright (c) 2007-2025 the FFmpeg developers built with gcc 15 (Ubuntu 15.2.0-13ubuntu3) configuration: --prefix=/usr --extra-version=3ubuntu2 --toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu --arch=amd64 --enable-gpl --disable-stripping --di | — |
| Docker Compose | **PASS** | Docker Compose version v5.4.0 | — |
| PyTorch CUDA | **WARN** | Traceback (most recent call last): File "<string>", line 1, in <module> import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda) ^^^^^^^^^^^^ ModuleNotFoundError: No module named 'torch' | Create a project virtual environment in Phase 1; use a PyTorch build that explicitly supports this GPU/driver. |
| Docker GPU | **PASS** | Sat Sep 19 09:02:10 2026 +-----------------------------------------------------------------------------------------+ \| NVIDIA-SMI 580.167.08 Driver Version: 580.167.08 CUDA Version: 13.0 \| +-----------------------------------------+------------------------+----------------------+ \| GPU Name Persistence-M \| Bus-Id Disp. | — |

## Phase 0 gate

**READY WITH WARNINGS.** No preflight hard-fail was found. Resolve applicable warnings before selecting the Phase 1 runtime.

## Compatibility recommendation (not applied)

- Do not change the NVIDIA driver or CUDA until `nvidia-smi` identifies a working GPU, driver version, and VRAM. Then select a CUDA-enabled PyTorch build whose published support matches that GPU and driver.
- Do **not** use the system Python 3.14 for ComfyUI today. Create an isolated Python 3.12 virtual environment for Phase 1, then pin ComfyUI and a compatible CUDA-enabled PyTorch build using their published release notes.
- Use Docker only after the explicit GPU smoke test passes; bind ComfyUI to `127.0.0.1` only.
- Before downloading any model, record source URL, exact revision, SHA-256, license, and intended weight in a model manifest. Only accept LoRA `.safetensors` files.

