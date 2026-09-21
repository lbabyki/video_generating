from fastapi import FastAPI

from app.core.config import settings
from app.api.errors import install_error_handlers
from app.api.governance import router as governance_router

app = FastAPI(title="Educational Video Studio", version="0.1.0")
install_error_handlers(app)
app.include_router(governance_router)


@app.get("/healthz")
def healthz() -> dict[str, str | bool]:
    return {"status": "ok", "comfyui_enabled": settings.comfyui_enabled}
