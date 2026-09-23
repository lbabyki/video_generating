# Phase 3D-E — CPU-only BI Overlay Smoke Test

Status: `OVERLAY_SMOKE_PASS_WITH_SCENE_VALIDATION_REQUIRED`

Exactly one Scene 1 diagnostic overlay MP4 was produced with FFmpeg/libx264 on
CPU. No Qwen, Ollama inference, ComfyUI, SDXL, LoRA, IP-Adapter, ControlNet,
audio, subtitle, or production render ran.

## Preflight

- Runtime resolver selected v5 package
  `4c8b44c1-b2e4-5f53-838c-bf844cfcbfad` with hash
  `2a83d0d9c08e41f21c138115ecc8d9fe937eea7619aa8aeb7151088a72eb00fa`.
- VisualBibleSet v2 `6d9297b4-b762-5b2c-90b1-54fd144592b5` is `APPROVED`.
- Registry asset `d63f1dec-1c7e-53aa-a5cd-e52b4522a26a` is
  `GREETING.png`, `APPROVED_FOR_REFERENCE`, alpha RGBA 500×500, and hash
  `94402e948108f7fff2e554c24e4c46380f816336e10c51e0a389582d536cfd83`.
- Source containment and symlink checks passed. The source remained outside the
  repository and unchanged.
- `ollama ps` was empty; ComfyUI and GPU workers were not started. FFmpeg and
  ffprobe were available.

## Render

- Scene: order 1, `Mở đầu: Cảnh đồng bằng Bắc Bộ`
- Binding: `GREETING`, right anchor, gentle entrance, no mirror, alpha required.
- Canvas: 1344×768, 30 fps, 5.000 seconds, neutral diagnostic background.
- Overlay scale: 169×169 (22% frame height); final position x=1121, y=430.
- Horizontal outer margin: 54 px (4%); subtitle-safe bottom zone: 138 px
  (18%). The mascot enters from the right over 0.6 seconds and then remains
  stable.
- Codec: H.264/libx264, `yuv420p`, one video stream, no audio, CPU-only.
- Output: `output/phase3d/overlay-smoke/scene-01-greeting/scene-01-greeting-overlay-smoke.mp4`
- SHA-256: `d0e57a69e200b52d6a1b535015270458f1b674c6ed0d30d1f4e8eed80c9add6d`
- Inference/render latency: 342 ms.
- QA frames at 0.2 s, 1.0 s, and 4.5 s are in the same ignored directory.

## Persistence and governance

- OverlayRenderAttempt: `eaab4d0f-9ed4-4edd-a22c-ae4078431f86`.
- Project-owner review by `40a6df62-f60a-439c-8509-890b9db2ee08`:
  `APPROVED_WITH_NOTES` at `2026-09-23T16:35:42.630092+00:00`.
- `technical_status=PASS`, `static_visual_review=PASS`,
  `motion_visual_review=PASS`, `overlay_smoke_status=PASS`,
  `human_review_status=APPROVED_WITH_NOTES`, `release_eligible=false`.
- Audit events: `OVERLAY_SMOKE_REVIEWED` recorded in reviewer and Bible audit
  logs. Review notes require collision/safe-area checks for every real scene;
  the mascot must not obscure faces, hands, safety actions, cultural evidence,
  or subtitles. Anchor/scale may change within approved limits.
- Database provenance includes package/Bible/asset IDs and hashes, source
  relative path, filter graph, geometry, FFmpeg version, output hash, latency,
  CPU-only flag, and ffprobe result.
- Mascot assets remain reference/runtime only; training permission remains
  `PENDING`. No package, Bible, binding, cultural decision, or lifecycle state
  was changed. This is not an overlay render pass, production approval,
  keyframe pass, LoRA pass, training-ready state, or prompt-to-video pass.

## Verification

- Full pytest: **133 passed** (one existing deprecation warning).
- Alembic: `0022_overlay_render_attempts (head)`.
- SQLite `foreign_key_check`: clean.
- `docker compose config --quiet`: passed.
- `git diff --check`: passed.
- Output and QA files are Git-ignored; no source asset is tracked or modified.
- This approval covers only the neutral diagnostic canvas. It is not
  `PRODUCTION_OVERLAY_APPROVED`, a keyframe pass, LoRA pass, training-ready
  state, or prompt-to-video pass.
