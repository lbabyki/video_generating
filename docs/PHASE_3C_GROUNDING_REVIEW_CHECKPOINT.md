# Phase 3C-B — Grounding Evidence and Visual Bible Review

Status: **GROUNDING_EVIDENCE_REGISTERED_PENDING_HUMAN_REVIEW**

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

## Phase 3C-C1 — confirmed source registration

The PDF author line was rechecked directly on page 1. The verified spelling is
**Đặng Tiên Dung**. The confirmed source was registered once from the relative
path in the proposal with source ID `57e76838-c1b0-5002-9305-e03742aaeec9`.
Its SHA-256 is
`b4ab4f60605827b404e16760a8c50ee28922bdd4b9da7a704dc0e066d972fd44`, MIME is
`application/pdf`, license is `UNKNOWN - no explicit license terms identified`,
and usage permission is `REFERENCE_ONLY`. It is not training eligible.

Five evidence links were created and remain `PENDING`:

- `2cbe899d-1abe-428f-85e8-913a62471da5` → terrain requirement
  `ac99933a-7d63-5e09-9f58-d5dbb489e4a3`.
- `2250c0d4-4738-48c4-a3d7-28e60a2384a6` → rice-field context requirement
  `890e4408-1e12-5714-ab4e-e436eaefab90`.
- `2c11faad-e519-4093-996b-57b9464c43bc` → river requirement
  `e0172286-ae9f-58b3-a69a-976b2d3d8e0e`.
- `3206c05b-d007-4533-a695-12dee1755410` → vegetation requirement
  `f9904c42-601e-52b0-8a43-68d6d4868442`.
- `57ae4372-bd55-472d-82cf-c395b4bc0b29` → nature-protection requirement
  `7ecff663-d790-57c7-85ba-61e9bdc6f05f`.

The school-architecture requirement
`c5eeed44-a93d-5378-b5d8-5ca85745e972` and Grade 4 clothing requirement
`e702d0e3-7998-5565-8bb6-017810b16eb3` have no evidence links and remain
`PENDING`/unmatched. All seven requirements remain `PENDING`, the bible is
still `DRAFT`, and all eight prompt packages remain unreleasable with
`keyframe_status=NOT_GENERATED`. No review decision, approval, or lock was
performed.
