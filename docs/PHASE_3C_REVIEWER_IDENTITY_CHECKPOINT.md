# Phase 3C-C2A — Local Human Reviewer Identity Bootstrap

Status: **REVIEWER_IDENTITY_RUNTIME_READY**

## Implementation

Migration `0013_human_reviewers` follows `0012_grounding_review` and creates
`HumanReviewer` plus `HumanReviewerAudit`. The local bootstrap script is
`scripts/bootstrap_local_reviewer.py` and accepts a user-provided display name
and one of `PROJECT_OWNER`, `CULTURAL_REVIEWER`, `CONTENT_REVIEWER`, or
`LEGAL_REVIEWER`.

Bootstrap creates a new UUID, `ACTIVE` status, provenance, and an audit event.
It is idempotent by normalized display name plus role, rejects empty names and
invalid roles, and never performs a review decision. The script was **not run
against the real database**, so no reviewer identity was created in this scope.

Review authorization requires an existing `ACTIVE` reviewer ID and an allowed
role. Inactive, revoked, missing, or role-incompatible IDs are rejected.
Project owners may review evidence, characters, environments, and project
design; cultural approval remains restricted to `CULTURAL_REVIEWER`.
Reviewer APIs expose only the ID/name/role/status needed by the MVP and no
internal provenance or local paths. This remains a local-only MVP and is not
appropriate for exposure on an untrusted network without authentication.

## Verification

Full pytest: **133 passed**. Alembic existing and clean databases reach
`0013_human_reviewers (head)`. SQLite foreign-key checks are clean, Docker
Compose configuration passed, and `git diff --check` passed.

No source, evidence, requirement, VisualBibleSet, prompt package, compilation,
or ProjectPlan data was changed. No Qwen, ComfyUI, SDXL, LoRA, image/video,
TTS, subtitle, download, scraping, or training operation was run. No commit or
push was made.
