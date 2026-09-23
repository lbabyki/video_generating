from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./data/studio.db"
    valkey_url: str = "redis://127.0.0.1:6379/0"
    storage_root: Path = Path("data/storage")
    comfyui_enabled: bool = False
    comfyui_url: str = "http://127.0.0.1:8188"
    prompt_planner_provider: str = os.getenv("PROMPT_PLANNER_PROVIDER", "mock").lower()
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:14b")
    ollama_timeout_seconds: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))
    ollama_keep_alive: str = os.getenv("OLLAMA_KEEP_ALIVE", "0")
    prompt_planner_temperature: float = float(os.getenv("PROMPT_PLANNER_TEMPERATURE", "0"))
    prompt_planner_seed: int = int(os.getenv("PROMPT_PLANNER_SEED", "314159"))
    prompt_template_version: str = os.getenv("PROMPT_TEMPLATE_VERSION", "phase3b-v4")
    prompt_planner_store_diagnostics: bool = os.getenv("PROMPT_PLANNER_STORE_DIAGNOSTICS", "false").lower() == "true"
    prompt_planner_diagnostics_dir: Path = Path(os.getenv("PROMPT_PLANNER_DIAGNOSTICS_DIR", "data/diagnostics/phase3b"))
    prompt_planner_allow_remote: bool = os.getenv("PROMPT_PLANNER_ALLOW_REMOTE", "false").lower() == "true"
    prompt_planner_max_gpu_utilization: int = int(os.getenv("PROMPT_PLANNER_MAX_GPU_UTILIZATION", "20"))
    prompt_planner_max_gpu_memory_mib: int = int(os.getenv("PROMPT_PLANNER_MAX_GPU_MEMORY_MIB", "4096"))


settings = Settings()
