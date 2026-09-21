from app.api.main import healthz


def test_healthz_is_cpu_safe() -> None:
    assert healthz() == {"status": "ok", "comfyui_enabled": False}
