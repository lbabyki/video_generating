from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class ComfyArtifact:
    filename: str
    subfolder: str
    kind: str


class ComfyUIClient:
    """HTTP contract only. It does not start ComfyUI or perform inference."""

    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.AsyncClient(base_url=self.base_url)

    async def submit(self, workflow: dict[str, Any], client_id: str) -> str:
        response = await self.client.post(f"{self.base_url}/prompt", json={"prompt": workflow, "client_id": client_id})
        response.raise_for_status()
        return response.json()["prompt_id"]

    async def history(self, prompt_id: str) -> dict[str, Any]:
        response = await self.client.get(f"{self.base_url}/history/{prompt_id}")
        response.raise_for_status()
        return response.json()

    async def progress(self, prompt_id: str) -> dict[str, Any]:
        history = await self.history(prompt_id)
        return {"prompt_id": prompt_id, "completed": prompt_id in history}

    async def cancel(self, prompt_id: str) -> None:
        response = await self.client.post(f"{self.base_url}/queue", json={"delete": [prompt_id]})
        response.raise_for_status()

    async def artifact(self, artifact: ComfyArtifact) -> bytes:
        response = await self.client.get(f"{self.base_url}/view", params=artifact.__dict__)
        response.raise_for_status()
        return response.content
