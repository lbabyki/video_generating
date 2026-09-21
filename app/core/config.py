from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./data/studio.db"
    valkey_url: str = "redis://127.0.0.1:6379/0"
    storage_root: Path = Path("data/storage")
    comfyui_enabled: bool = False
    comfyui_url: str = "http://127.0.0.1:8188"


settings = Settings()
