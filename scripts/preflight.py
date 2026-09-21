#!/usr/bin/env python3
"""Read-only reproducible preflight for the Educational Video Studio.

This script does not install packages, pull models, change drivers, or alter
Docker configuration.  It exits non-zero only when a required preflight check
fails; warnings remain visible in the generated Markdown report.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Check:
    name: str
    status: str
    evidence: str
    remedy: str = ""


def run(*cmd: str, timeout: int = 20) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout)
        return proc.returncode, proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, f"{type(exc).__name__}: {exc}"


def one_line(text: str, limit: int = 320) -> str:
    return " ".join(text.split())[:limit] or "(no output)"


def binary_version(binary: str, required: bool = True, version_arg: str = "--version") -> Check:
    path = shutil.which(binary)
    if not path:
        return Check(binary, "FAIL" if required else "WARN", "not found",
                     f"Install {binary} using your approved OS package workflow.")
    code, out = run(binary, version_arg)
    if code:
        return Check(binary, "WARN", f"{path}; {one_line(out)}")
    return Check(binary, "PASS", f"{path}; {one_line(out)}")


def disk_check() -> Check:
    root = Path.cwd().anchor or "/"
    usage = shutil.disk_usage(root)
    free_gib = usage.free / 1024**3
    status = "PASS" if free_gib >= 150 else "WARN" if free_gib >= 80 else "FAIL"
    return Check("Workspace disk", status,
                 f"{free_gib:.1f} GiB free of {usage.total / 1024**3:.1f} GiB at {root}",
                 "Free or add at least 150 GiB before storing approved models and renders."
                 if status != "PASS" else "")


def nvidia_check() -> Check:
    code, out = run("nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                    "--format=csv,noheader")
    if code:
        _, pci = run("lspci", "-nn")
        gpu = next((line.strip() for line in pci.splitlines()
                    if "NVIDIA" in line and ("VGA" in line or "3D" in line)), "NVIDIA GPU not identified")
        _, module = run("modinfo", "-F", "version", "nvidia")
        module_text = f"; loaded module version {module.strip()}" if module.strip() else ""
        return Check("NVIDIA GPU / driver", "FAIL", one_line(f"{gpu}{module_text}; nvidia-smi: {out}"),
                     "First reboot and rerun this report. If it still fails, have the system administrator reconcile the NVIDIA userspace packages and kernel module against the current kernel using the NVIDIA/Ubuntu compatibility matrix; do not change CUDA or driver speculatively.")
    return Check("NVIDIA GPU / driver", "PASS", one_line(out))


def cpu_check() -> Check:
    code, out = run("lscpu")
    if code:
        return Check("CPU", "PASS", f"{os.cpu_count() or 0} logical CPUs; model unavailable")
    fields = dict(re.findall(r"^([^:]+):\s*(.+)$", out, flags=re.MULTILINE))
    model = fields.get("Model name", "model unavailable")
    logical = fields.get("CPU(s)", str(os.cpu_count() or 0))
    cores = fields.get("Core(s) per socket")
    sockets = fields.get("Socket(s)")
    physical = f"; {cores} cores × {sockets} socket(s)" if cores and sockets else ""
    return Check("CPU", "PASS", f"{model}; {logical} logical CPUs{physical}")


def storage_device_check() -> Check:
    code, out = run("lsblk", "-dn", "-o", "NAME,TYPE,ROTA,MODEL,SIZE")
    if code:
        return Check("Storage device", "WARN", one_line(out), "Confirm the workspace resides on SSD/NVMe storage.")
    disks = []
    for line in out.splitlines():
        parts = line.split(None, 4)
        if len(parts) >= 4 and parts[1] == "disk" and parts[2] == "0":
            disks.append(line.strip())
    if disks:
        return Check("Storage device", "PASS", "; ".join(disks))
    return Check("Storage device", "WARN", one_line(out), "Confirm the workspace resides on SSD/NVMe storage.")


def pytorch_check() -> Check:
    code, out = run(sys.executable, "-c", "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda)")
    if code:
        return Check("PyTorch CUDA", "WARN", one_line(out),
                     "Create a project virtual environment in Phase 1; use a PyTorch build that explicitly supports this GPU/driver.")
    values = out.splitlines()
    if len(values) >= 2 and values[1].strip() == "True":
        return Check("PyTorch CUDA", "PASS", one_line(out))
    return Check("PyTorch CUDA", "FAIL", one_line(out),
                 "Use an approved CUDA-enabled PyTorch build in an isolated virtual environment.")


def docker_gpu_check(enabled: bool) -> Check:
    if not shutil.which("docker"):
        return Check("Docker GPU", "WARN", "Docker not installed")
    code, out = run("docker", "info", "--format", "{{.ServerVersion}}")
    if code:
        return Check("Docker GPU", "WARN", one_line(out),
                     "The current session cannot access Docker. If the account was added to the docker group, start a fresh login session; otherwise have an administrator grant access, then retry.")
    if not enabled:
        return Check("Docker GPU", "WARN", "not executed (run with --docker-gpu)",
                     "Run the explicit container smoke test before choosing a containerized Phase 1 setup.")
    code, out = run("docker", "run", "--rm", "--gpus", "all",
                    "nvidia/cuda:12.4.1-base-ubuntu22.04", "nvidia-smi", timeout=180)
    return Check("Docker GPU", "PASS" if code == 0 else "FAIL", one_line(out),
                 "Install/configure NVIDIA Container Toolkit and retry; do not alter the host driver solely for this test."
                 if code else "")


def system_checks(docker_gpu: bool) -> list[Check]:
    checks: list[Check] = []
    checks.append(Check("Operating system", "PASS", f"{platform.platform()}"))
    checks.append(cpu_check())
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        total = next((x for x in meminfo.read_text().splitlines() if x.startswith("MemTotal:")), "")
        checks.append(Check("RAM", "PASS", total.replace("MemTotal:", "").strip()))
    checks.append(disk_check())
    checks.append(storage_device_check())
    checks.append(nvidia_check())
    for binary in ("git", "docker", "python3", "node"):
        checks.append(binary_version(binary))
    checks.append(binary_version("ffmpeg", version_arg="-version"))
    checks.append(binary_version("ffprobe", version_arg="-version"))
    compose = binary_version("docker-compose", required=False)
    if compose.status != "PASS":
        code, out = run("docker", "compose", "version")
        compose = Check("Docker Compose", "PASS" if code == 0 else "FAIL", one_line(out),
                        "Install Docker Compose v2 plugin." if code else "")
    else:
        compose.name = "Docker Compose"
    checks.append(compose)
    checks.append(pytorch_check())
    checks.append(docker_gpu_check(docker_gpu))
    return checks


def markdown(checks: list[Check]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = ["| Check | Status | Evidence | Safe remediation |", "|---|---|---|---|"]
    for c in checks:
        rows.append(f"| {c.name} | **{c.status}** | {c.evidence.replace('|', '\\|')} | {c.remedy.replace('|', '\\|') or '—'} |")
    statuses = {s: sum(c.status == s for c in checks) for s in ("PASS", "WARN", "FAIL")}
    blockers = [c for c in checks if c.status == "FAIL"]
    body = ["# Phase 0 — Preflight Report", "", f"Generated: `{now}`", "",
            f"Summary: **{statuses['PASS']} PASS / {statuses['WARN']} WARN / {statuses['FAIL']} FAIL**.", "",
            *rows, "", "## Phase 0 gate", ""]
    if blockers:
        body += ["**NOT READY for Phase 1.** Resolve the FAIL items below, then rerun:", "", "```bash", "python3 scripts/preflight.py --docker-gpu", "```", ""]
        body += [f"- **{c.name}:** {c.evidence}. {c.remedy}" for c in blockers]
    else:
        body += ["**READY WITH WARNINGS.** No preflight hard-fail was found. Resolve applicable warnings before selecting the Phase 1 runtime."]
    body += ["", "## Compatibility recommendation (not applied)", "",
             "- Do not change the NVIDIA driver or CUDA until `nvidia-smi` identifies a working GPU, driver version, and VRAM. Then select a CUDA-enabled PyTorch build whose published support matches that GPU and driver.",
             "- Do **not** use the system Python 3.14 for ComfyUI today. Create an isolated Python 3.12 virtual environment for Phase 1, then pin ComfyUI and a compatible CUDA-enabled PyTorch build using their published release notes.",
             "- Use Docker only after the explicit GPU smoke test passes; bind ComfyUI to `127.0.0.1` only.",
             "- Before downloading any model, record source URL, exact revision, SHA-256, license, and intended weight in a model manifest. Only accept LoRA `.safetensors` files.", ""]
    return "\n".join(body) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docker-gpu", action="store_true", help="run an explicit NVIDIA CUDA Docker smoke test (may pull a public CUDA test image)")
    parser.add_argument("--output", type=Path, default=Path("docs/PREFLIGHT_REPORT.md"))
    args = parser.parse_args()
    checks = system_checks(args.docker_gpu)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown(checks), encoding="utf-8")
    print(args.output)
    for check in checks:
        print(f"{check.status:4} {check.name}: {check.evidence}")
    return 1 if any(c.status == "FAIL" for c in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
