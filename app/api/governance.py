from fastapi import APIRouter
from pydantic import BaseModel

from app.api.errors import APIError
from app.governance.service import CulturalProfile, Scene

router = APIRouter(prefix="/governance", tags=["governance"])
profiles = {"northern-delta": CulturalProfile("northern-delta", 1, "APPROVED", "Northern Delta Visual Profile v1.0")}
scenes: dict[str, Scene] = {}


class ReviewRequest(BaseModel):
    kind: str
    decision: str


@router.get("/cultural-profiles/{name}")
def get_cultural_profile(name: str) -> CulturalProfile:
    if name not in profiles:
        raise APIError("NOT_FOUND", "Cultural profile not found", 404)
    return profiles[name]


@router.post("/scenes/{scene_id}/reviews")
def create_review(scene_id: str, request: ReviewRequest) -> Scene:
    scene = scenes.get(scene_id, Scene(scene_id))
    try:
        scenes[scene_id] = scene.review(request.kind, request.decision)
    except ValueError as exc:
        raise APIError("INVALID_REVIEW", str(exc)) from exc
    return scenes[scene_id]


@router.post("/scenes/{scene_id}/reviews/approve")
def approve_review(scene_id: str, kind: str) -> Scene:
    return create_review(scene_id, ReviewRequest(kind=kind, decision="APPROVED"))


@router.post("/scenes/{scene_id}/reviews/reject")
def reject_review(scene_id: str, kind: str) -> Scene:
    return create_review(scene_id, ReviewRequest(kind=kind, decision="REJECTED"))


@router.post("/scenes/{scene_id}/approve")
def approve_scene(scene_id: str) -> Scene:
    scene = scenes.get(scene_id, Scene(scene_id))
    try:
        while scene.state != "APPROVED":
            scene = scene.transition()
    except ValueError as exc:
        raise APIError("INVALID_TRANSITION", str(exc)) from exc
    scenes[scene_id] = scene
    return scene


@router.post("/scenes/{scene_id}/lock")
def lock_scene(scene_id: str) -> Scene:
    scene = scenes.get(scene_id)
    if scene is None:
        raise APIError("NOT_FOUND", "Scene not found", 404)
    try:
        scenes[scene_id] = scene.lock()
    except ValueError as exc:
        raise APIError("RELEASE_BLOCKED", str(exc), 409) from exc
    return scenes[scene_id]


@router.post("/scenes/{scene_id}/release-render")
def release_render(scene_id: str) -> dict[str, str]:
    scene = scenes.get(scene_id)
    if scene is None or not scene.can_release_render():
        raise APIError("RELEASE_BLOCKED", "Only LOCKED scenes with both reviews may render", 409)
    return {"status": "eligible"}
