#!/usr/bin/env python3
"""Real local-only Phase 1A ComfyUI smoke test; performs no inference."""

import json
import subprocess
import sys
import time
from urllib.request import urlopen


def docker(*args: str) -> str:
    return subprocess.run(["docker", "compose", "--profile", "gpu", *args], text=True, capture_output=True, check=True).stdout


def main() -> int:
    container_id = docker("ps", "-q", "comfyui").strip()
    if not container_id:
        raise RuntimeError("ComfyUI container is not running")
    inspection = json.loads(subprocess.run(["docker", "inspect", container_id], text=True, capture_output=True, check=True).stdout)[0]
    if inspection["State"]["Status"] != "running" or inspection["State"].get("Health", {}).get("Status") != "healthy":
        raise RuntimeError(f"container is not healthy: {inspection['State']}")
    port = inspection["NetworkSettings"]["Ports"].get("8188/tcp", [])
    if len(port) != 1 or port[0].get("HostIp") != "127.0.0.1":
        raise RuntimeError(f"ComfyUI must only publish localhost: {port}")
    for _ in range(5):
        try:
            with urlopen("http://127.0.0.1:8188/system_stats", timeout=5) as response:
                if response.status != 200:
                    raise RuntimeError(f"unexpected HTTP status {response.status}")
                payload = json.loads(response.read())
                break
        except OSError:
            time.sleep(1)
    else:
        raise RuntimeError("/system_stats was not reachable")
    payload_text = json.dumps(payload).lower()
    if "cuda" not in payload_text and "nvidia" not in payload_text:
        raise RuntimeError("/system_stats did not identify CUDA/NVIDIA")
    logs = docker("logs", "--tail=100", "comfyui").lower()
    if "cuda out of memory" in logs or "cuda oom" in logs:
        raise RuntimeError("ComfyUI logs contain CUDA OOM")
    print("PASS ComfyUI healthy, localhost-only, and CUDA/NVIDIA visible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
