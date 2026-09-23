# Phase 3C-B — Grounding Evidence and Visual Bible Review

Status: **GROUNDING_REVIEW_RUNTIME_READY**

## Scope

This phase extends the existing `ReferenceSource` provenance with source
category, usage permission, local file hash/MIME metadata, and review state. It
adds `EvidenceLink`, human `VisualBibleReview`, and append-only audit records.
No source is fabricated, downloaded, scraped, copied into Git, or automatically
approved. No Qwen, ComfyUI, SDXL, LoRA, image, video, TTS, subtitle, or model
download/inference was run.

## Grounding state

VisualBibleSet `9f2272dd-2237-53ed-a3aa-fd570e89a75e` retains its existing DRAFT
version. Its seven requirements remain **PENDING** with
`review_required=true`; no evidence or source was registered. The two
CharacterBible and four EnvironmentBible reviews remain pending, so approval,
cultural approval, and locking are blocked.

Supported source types are `FACTUAL_REFERENCE`, `CULTURAL_REFERENCE`,
`VISUAL_REFERENCE`, and `TRAINING_ASSET`. Only `TRAINING_ALLOWED` can be used
for training. `REFERENCE_ONLY`, `UNKNOWN`, `BLOCKED`, and
`REQUIRES_LEGAL_REVIEW` cannot be exported to training. A human reviewer,
page/section, and short paraphrased evidence summary are required before an
EvidenceLink can support a requirement.

## Security and API

Local registration accepts only PDF, PNG, JPEG, and WebP files below the
configured reference root. It resolves paths before opening, rejects traversal
and escaping symlinks, checks size and magic bytes against the extension, and
stores a deterministic SHA-256. Duplicate hashes are idempotent. API responses
never expose absolute local paths.

Added endpoints include local source registration, source lookup, evidence
creation/review, grounding view, character/environment/cultural review, and
the existing bible approve/lock transitions. Any source/evidence/bible change
invalidates approval state and all prompt packages; LOCKED sets are immutable.

Manifest template: `fixtures/phase3c_grounding/source_manifest.example.json`.

## Persistence and verification

Migration `0012_grounding_review` follows `0011_visual_bibles`. Full pytest:
**129 passed**. Clean Alembic upgrade/current, SQLite foreign-key checks,
Docker Compose configuration, and `git diff --check` passed. The source
compilation, ProjectPlan, VisualBibleSet version, and four failed compilations
were not modified.

This checkpoint does not claim `GROUNDED`, `CULTURAL_APPROVED`,
`VISUAL_BIBLE_APPROVED`, `KEYFRAME_PASS`, or `PROMPT_TO_VIDEO_PASS`.
