from fastapi import FastAPI

from app.core.config import settings
from app.api.errors import install_error_handlers
from app.api.governance import router as governance_router
from app.api.prompt_compilations import router as prompt_compilations_router
from app.api.visual_bibles import router as visual_bibles_router
from app.api.grounding import router as grounding_router

app = FastAPI(title="Educational Video Studio", version="0.1.0")
install_error_handlers(app)
app.include_router(governance_router)
app.include_router(prompt_compilations_router)
app.include_router(visual_bibles_router)
app.include_router(grounding_router)


@app.get("/healthz")
def healthz() -> dict[str, str | bool]:
    return {"status": "ok", "comfyui_enabled": settings.comfyui_enabled}
