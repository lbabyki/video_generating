# Phase 3C-B — Grounding Evidence and Visual Bible Review

Status: **GROUNDING_PARTIALLY_REVIEWED_MISSING_EVIDENCE**

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

Migrations `0012_grounding_review`, `0013_human_reviewers`, and
`0014_grounding_requirement_followup` follow the earlier visual bible tables.
The latest full pytest is **133 passed**. Clean Alembic upgrade/current, SQLite foreign-key checks,
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

## Phase 3C-C2 — human review and missing references

Reviewer preflight verified reviewer ID
`40a6df62-f60a-439c-8509-890b9db2ee08` as `ACTIVE` with role
`PROJECT_OWNER`. Five existing evidence links were resolved by
`grounding_requirement_id` and reviewed without changing their summaries:

- terrain: `SUPPORTED`;
- rice-field context: `PARTIALLY_SUPPORTED`, `needs_more_evidence=true`;
- river: `SUPPORTED`;
- vegetation/landscape: `PARTIALLY_SUPPORTED`, `needs_more_evidence=true`;
- nature-protection actions: `SUPPORTED`.

Three metadata-only URL sources were added, all `REFERENCE_ONLY` and not
training eligible: TCVN 8793:2011 (`792b1cea-ae19-5547-b229-8ef3681126ff`),
Trường Tiểu học Khương Mai (`65e59124-e45c-51cc-8d1a-e72e982b8a7a`), and
Nghi thức Đội TNTP Hồ Chí Minh (`3cb84bc8-578a-50c7-aa3d-90d8c596c7ff`). No
remote URL was fetched. The project-owned uniform PDF was registered as
`e2e5808c-3c21-5c00-a66c-3da26af706a6`, with SHA-256
`1854c8ee68d32992e44ec2448e9a4c51b80102326e13694011edd4eebb0af0d5`,
`PROJECT_OWNED` license, and `REFERENCE_ONLY` permission.

Four new evidence links were added: two school-architecture links remain
`PENDING`; the uniform project-design link is `SUPPORTED` by the project owner
while the Nghi thức Đội link remains `PENDING`. The clothing requirement is
therefore still `PENDING`; the school requirement is still `PENDING`. All seven
requirements are not complete, the bible remains `DRAFT`, all eight packages
remain unreleasable with `NOT_GENERATED` keyframes, and no approval or lock was
performed. VisualBibleAudit contains the source/evidence/review events.

## Phase 3C-C2B — additional human review

Reviewer `40a6df62-f60a-439c-8509-890b9db2ee08` (`ACTIVE`, `PROJECT_OWNER`)
confirmed three additional evidence decisions: TCVN 8793:2011 is
`SUPPORTED`, the Khương Mai school website is `PARTIALLY_SUPPORTED`, and the
Nghi thức Đội source is `SUPPORTED`. The school requirement remains `PENDING`
with `needs_more_evidence=true` because one of its two sources is partial.
The clothing requirement is now `SUPPORTED` because both its project-owned
design evidence and the Nghi thức Đội evidence are supported.

The same reviewer approved the two recurring CharacterBible reviews and three
EnvironmentBible design reviews: low flat rice fields without terraces or
mountains, common vegetation without asserting a species, and a simple modern
primary school with yard/trees and no foreign or palace architecture. The
riverbank EnvironmentBible and cultural review remain unapproved. The two
partial requirements for rice fields and vegetation retain
`needs_more_evidence=true`; VisualBibleSet remains `DRAFT`, packages remain
unreleasable, and no lock or final approval was performed.

## Phase 3C-C2C — Restricted-scope grounding resolution

Status: `GROUNDING_RESOLVED_VISUAL_PROMPTS_IN_REVIEW`

- Reviewer `40a6df62-f60a-439c-8509-890b9db2ee08` resolved seven requirements with restricted-scope records; factual partial links remain marked `PARTIALLY_SUPPORTED`.
- Project-owned visual design source: `lesson08-red-river-delta/documents/project-owned/environment_design_decision_v1.pdf`, registered as `VISUAL_REFERENCE`, `PROJECT_OWNED`, `REFERENCE_ONLY`; it is not training evidence.
- Rice, vegetation, school design scopes and exclusions are persisted in `grounding_resolutions`; no unsupported species, architecture, terrain, uniform generalization, or historical claims were added.
- Riverbank EnvironmentBible review is `APPROVED`; all four EnvironmentBibles and both CharacterBibles are approved for this review stage. Cultural review remains `PENDING`.
- Eight prior v1 prompt packages remain immutable and are `SUPERSEDED`; eight deterministic v2 packages are `ACTIVE`, `DRAFT`, `release_eligible=false`, `keyframe_status=NOT_GENERATED`.
- VisualBibleSet is `IN_REVIEW`. It is not `APPROVED` or `LOCKED`; prompt-to-image/video/audio generation has not run.

## Phase 3C-C2D — Visual Prompt Semantic QA and Role Scoping

Status: `VISUAL_PROMPT_V3_READY_FOR_HUMAN_REVIEW`

- Character-role audit found the original teacher binding missing. Deterministic DRAFT teacher CharacterBible `c92a7bf1-39c0-5d6d-83c5-159d77a44d96` was added; it was not approved. Scene 3 now binds teacher + student, and Scene 4 binds teacher supervision + student.
- Student, community adult, and teacher wardrobe instructions are role-scoped. Only the recurring student receives the approved red scarf/white collared shirt/navy trousers/simple shoes design.
- Eight v2 packages remain preserved as `SUPERSEDED`; eight deterministic v3 packages are `ACTIVE`, `DRAFT`, unreleasable and keyframe-free.
- v3 packages use structured style/environment/subject/action/composition/camera/lighting/continuity/workflow metadata. Model-facing prompts contain natural-language flat lowland descriptions and no UUIDs.
- VisualBibleSet remains `IN_REVIEW`; cultural review remains `PENDING`. No CHARACTER_CONSISTENCY_PASS, VISUAL_BIBLE_APPROVED, KEYFRAME_PASS or PROMPT_TO_VIDEO_PASS is claimed.

## Phase 3C-C2E — Final Visual Prompt Lock Readiness

Status: `VISUAL_PROMPT_V4_LOCK_READINESS_REVIEW`

- SDXL Base registry record and local checkpoint matched: revision `462165984030d82259a11f4367a4eed129e94a7b`, SHA-256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`, architecture `SDXL_BASE`.
- Student CharacterBible v2 records the approved restricted Đội viên wardrobe; v1 remains preserved. Teacher remains `DRAFT` with a pending human review checklist.
- Background student and community-adult cohorts are metadata descriptors without persistent UUID identities.
- Eight v1, v2 and v3 packages remain preserved as `SUPERSEDED`; eight deterministic v4 packages are `ACTIVE`, DRAFT, unreleasable and keyframe-free.
- V4 separates static keyframe prompts from motion intent, camera motion and transition metadata. Model-facing prompts contain natural language camera descriptions and no internal UUID/hash/governance tokens.
- VisualBibleSet remains `IN_REVIEW`; cultural review remains `PENDING`. No inference or media generation ran.

## Phase 3C-C2E — Confirmation and role-scoped lock gate

- Reviewer `40a6df62-f60a-439c-8509-890b9db2ee08` approved the teacher CharacterBible within the authorized `PROJECT_OWNER` character-review scope. The decision scope and timestamp are stored in `VisualBibleReview` and audit records.
- Student uniform remains approved with restricted Đội viên scope; background students do not inherit the red scarf by default.
- The requested cultural approval was not recorded because this reviewer is `PROJECT_OWNER` and the cultural endpoint requires an active `CULTURAL_REVIEWER`. A role-gate audit was recorded; cultural review remains `PENDING`.
- VisualBibleSet remains `IN_REVIEW`; no APPROVED/LOCKED transition, render lock, keyframe, media generation, or inference was performed.

## Phase 3C-C2F — Cultural Review and Content Approval

Status: `CONTENT_APPROVED`

- Cultural reviewer `241e7b2d-9d76-4caa-97d8-9796478a5fa0` was verified ACTIVE with role `CULTURAL_REVIEWER` and recorded `APPROVED_WITH_RESTRICTED_SCOPE` with timestamp and scope.
- Teacher CharacterBible, student v2 CharacterBible, four EnvironmentBibles, seven GroundingResolution records, and eight active v4 packages passed the approval gate.
- VisualBibleSet transitioned from `IN_REVIEW` to `APPROVED` as content approval only. `release_eligible=false`; no render lock or production lock was created.
- v1/v2/v3 packages remain preserved as `SUPERSEDED`; v4 remains `ACTIVE`, DRAFT, keyframe-free, and unreleasable.
- LoRA status remains `NOT_ASSIGNED`; reference status remains `NOT_GENERATED`; consistency readiness remains `PROMPT_ONLY`.
- No Qwen, ComfyUI, SDXL, LoRA, TTS, video inference, keyframe generation, or media generation ran.
