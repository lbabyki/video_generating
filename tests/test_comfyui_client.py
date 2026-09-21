import unittest

import httpx

from app.comfyui_client import ComfyArtifact, ComfyUIClient


class ComfyUIClientContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_contract_against_mock_transport(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/prompt":
                return httpx.Response(200, json={"prompt_id": "p-1"})
            if request.url.path == "/history/p-1":
                return httpx.Response(200, json={"p-1": {"status": "success"}})
            if request.url.path == "/queue":
                return httpx.Response(200, json={})
            if request.url.path == "/view":
                return httpx.Response(200, content=b"png")
            return httpx.Response(404)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            client = ComfyUIClient("http://mock", http)
            prompt_id = await client.submit({"1": {}}, "client-1")
            self.assertEqual(prompt_id, "p-1")
            self.assertTrue((await client.progress(prompt_id))["completed"])
            await client.cancel(prompt_id)
            self.assertEqual(await client.artifact(ComfyArtifact("a.png", "", "output")), b"png")
