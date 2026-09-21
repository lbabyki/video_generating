from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def test_comfyui_compose_is_local_gpu_profile() -> None:
    config = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    comfy = config["services"]["comfyui"]
    assert comfy["profiles"] == ["gpu"]
    assert comfy["gpus"] == "all"
    assert comfy["ports"] == ["127.0.0.1:8188:8188"]
    assert "pending-gpu-preflight" not in comfy["image"]
    assert comfy["healthcheck"]["test"][0] == "CMD"
    assert "/system_stats" in " ".join(comfy["healthcheck"]["test"])
    assert "privileged" not in comfy
    assert all("docker.sock" not in mount for mount in comfy["volumes"])
    assert comfy["volumes"] == [
        "./models/checkpoints:/opt/ComfyUI/models/checkpoints",
        "./models/loras:/opt/ComfyUI/models/loras",
        "./models/vae:/opt/ComfyUI/models/vae",
        "./models/controlnet:/opt/ComfyUI/models/controlnet",
        "./models/clip_vision:/opt/ComfyUI/models/clip_vision",
        "./input:/opt/ComfyUI/input",
        "./output:/opt/ComfyUI/output",
        "./user:/opt/ComfyUI/user",
    ]


def test_comfyui_dockerfile_is_pinned_and_nonroot() -> None:
    dockerfile = (ROOT / "docker/comfyui/Dockerfile").read_text()
    lockfile = (ROOT / "docker/comfyui/requirements.lock").read_text()
    revision = (ROOT / "docker/comfyui/COMFYUI_REVISION").read_text().strip()
    assert revision in dockerfile
    assert "requirements.lock" in dockerfile
    assert "torch==2.11.0+cu128" in lockfile
    assert "torchaudio==2.11.0+cu128" in lockfile
    assert "USER comfyui" in dockerfile
    assert '"main.py"' in dockerfile and '"--listen"' in dockerfile
