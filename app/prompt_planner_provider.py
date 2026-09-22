from app.core.config import settings
from app.ollama_prompt_planner import OllamaQwenPromptPlanner
from app.prompt_compiler import DeterministicMockPromptPlanner, PromptPlanner


def configured_prompt_planner() -> PromptPlanner:
    if settings.prompt_planner_provider == "mock":
        return DeterministicMockPromptPlanner()
    if settings.prompt_planner_provider == "ollama":
        return OllamaQwenPromptPlanner()
    raise ValueError("PROMPT_PLANNER_PROVIDER must be mock or ollama")
