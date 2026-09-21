from app.api.governance import approve_scene, create_review, lock_scene, release_render, scenes
from app.api.governance import ReviewRequest
from app.api.errors import APIError


def test_release_is_blocked_without_cultural_review() -> None:
    scene_id = "api-release-blocked"
    scenes.pop(scene_id, None)
    approve_scene(scene_id)
    try:
        lock_scene(scene_id)
    except APIError as exc:
        assert exc.code == "RELEASE_BLOCKED"
    else:
        raise AssertionError("lock must be blocked")


def test_approved_scene_can_lock_and_release() -> None:
    scene_id = "api-release-ok"
    scenes.pop(scene_id, None)
    create_review(scene_id, ReviewRequest(kind="content", decision="APPROVED"))
    create_review(scene_id, ReviewRequest(kind="cultural", decision="APPROVED"))
    approve_scene(scene_id)
    assert lock_scene(scene_id).state == "LOCKED"
    assert release_render(scene_id) == {"status": "eligible"}
