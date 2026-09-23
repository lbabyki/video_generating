# Phase 3C-A — Grounded Character and Environment Bible Foundation

Status: **VISUAL_BIBLE_FOUNDATION_READY**

## Scope

Phase 3C-A materializes grounded visual bible data from successful compilation
`88e6c89b-8924-4661-b7ec-c3d73cc9d4ba`. It does not modify the source
`ProjectPlan`, compilation provenance, or the four historical failed
compilations. No Qwen, ComfyUI, SDXL, LoRA, image, video, TTS, subtitle, model
download, or keyframe inference was run.

## Materialized DRAFT

- VisualBibleSet: `9f2272dd-2237-53ed-a3aa-fd570e89a75e`
- Version/status: `1` / `DRAFT`
- Source plan hash is persisted and checked before approval/lock.
- CharacterBible: **2** stable character IDs.
- EnvironmentBible: **4** — 1 regional profile and 3 scene locations.
- SceneVisualBinding: **8**.
- VisualPromptPackage: **8** deterministic packages.
- GroundingRequirement: **7**, all `PENDING` with `review_required=true`.
- All packages are `DRAFT`, `release_eligible=false`, `keyframe_status=NOT_GENERATED`, with no LoRA IDs or source references.

Regional profile is `red-river-delta`, terrain `flat_delta`, profile ID
`ff0c1615-3aac-5901-94df-6a00ca731063`. The three locations are the rice field,
riverbank, and school from the source plan. Scene bindings preserve source plan
hash, regional profile, character/environment bible versions, and deterministic
binding hashes. Character and location IDs are never accepted from model output
as final identities.

## Governance

Materialization is insert-only and idempotent for a compilation. Approval and
lock are blocked while grounding requirements or cultural review remain pending,
when the source plan hash changes, or when the source compilation is not
`SUCCEEDED`. Locked sets are immutable at the service boundary. Invalidating a
set marks all visual prompt packages invalid.

## Persistence and verification

Migration `0011_visual_bibles` follows `0010_candidate_timeline_observability`.
Full pytest: **126 passed**. API smoke against the successful compilation
returned the same DRAFT set with 2 characters, 4 environments, 8 bindings, 8
packages, and 7 grounding requirements. Clean Alembic upgrade/current reached
`0011_visual_bibles`; SQLite foreign-key checks are clean; Docker Compose
configuration and `git diff --check` passed.

This checkpoint does not claim `KEYFRAME_PASS`, `CULTURAL_APPROVED`, or
`PROMPT_TO_VIDEO_PASS`.
