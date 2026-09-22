# Phase 3A — Prompt Compiler and Scene Schema

Status: **PROMPT_COMPILER_FOUNDATION_READY**. This phase converts Vietnamese
text requests into a validated, persisted storyboard draft using only a local
deterministic mock planner.

## Scope and schemas

`PromptCompilationRequest` rejects blank/oversized prompts, invalid duration,
unsupported language or enum values, wrong types, and extra fields. Prompt size,
duration bounds, and duration tolerance can be configured with
`PROMPT_COMPILER_MAX_LENGTH`, `PROMPT_COMPILER_MIN_DURATION`,
`PROMPT_COMPILER_MAX_DURATION`, and `PROMPT_COMPILER_DURATION_TOLERANCE`.
Prompt text is data; no prompt string is evaluated, executed, or passed to a
model. Raw text and whitespace-normalized request are stored separately.

`ProjectPlan` schema version `1.0` includes character and environment reference
records plus ordered `ScenePlan` entries. Validation checks continuous unique
scene numbering, 3–8 second scene durations, total duration tolerance,
character/environment references, nonempty narration, prompt-draft model/path
exclusion, and source references before allowing `GROUNDED`. Compiler drafts
always have DRAFT governance, pending content/cultural review, no keyframes,
unlocked scenes, and `release_eligible=false`.

The current local fixture uses a stable Red River Delta profile and forbids
high mountains, stilt-house villages, and Chinese/Japanese palace architecture.
If a prompt gives only a generic Vietnam setting or historical content without
time/place grounding, it is marked `NEEDS_REVIEW` with a warning. Conflicting
cultural cues are also marked `NEEDS_REVIEW`.

## Planner and persistence

`PromptPlanner` is the extension point for later planners.
`DeterministicMockPromptPlanner` performs no network access and has no model
dependencies. No Qwen or Ollama was downloaded or run; no inference occurred.

Migration `0007_prompt_compilations` follows head `0006_dataset_governance`.
Existing project/scene tables did not exist in this repository, so the
compilation request and versioned plan are stored once in `prompt_compilations`
rather than adding duplicate Project or Scene entities. The table stores raw
prompt, normalized request, planner/schema/profile versions, deterministic
request hash, compiled plan, warnings, governance state, and timestamps. The
unique request hash makes retries idempotent.

## API

- `POST /prompt-compilations`
- `GET /prompt-compilations/{id}`
- `GET /prompt-compilations/{id}/plan`
- `POST /prompt-compilations/{id}/validate`
- `POST /prompt-compilations/{id}/approve-storyboard`
- `PATCH /prompt-compilations/{id}/scenes/{scene_number}`

The approval endpoint advances storyboard governance only to
`STORYBOARD_APPROVED`; content, cultural, keyframe, and release approvals remain
pending/false. The service is intended to run locally (Uvicorn's default bind
is loopback); no Internet exposure or remote service was configured.
Editing a scene validates the full plan, returns governance to DRAFT, and
invalidates content/cultural approvals and lock state from that scene onward.

## Golden fixture

`fixtures/phase_3a_golden_request.json` describes the original project prompt
“Bảo vệ thiên nhiên” for Grade 4 History and Geography, 45 seconds, 16:9, in
the contemporary Red River Delta. `fixtures/phase_3a_golden_output.json`
contains the reproducible eight-scene plan. Its scenes total 45 seconds, reuse
stable character/environment IDs, request no references (therefore remain
ungrounded), and contain no generated keyframes.

## Validation and execution results

- Pytest: **47 passed** (1 upstream Starlette deprecation warning).
- Clean SQLite Alembic upgrade: **PASS**, head `0007_prompt_compilations`.
- Application SQLite `PRAGMA foreign_keys`: **1**.
- `docker compose config --quiet`: **PASS**.
- API create/get/plan/validate/storyboard-approval smoke via FastAPI TestClient:
  **PASS**.
- ComfyUI health smoke: **PASS**, healthy, bound to localhost, CUDA/NVIDIA
  visible, no CUDA OOM in the checked log tail. The existing pinned image was
  started for this smoke; no ComfyUI/CUDA/model configuration was changed and
  no inference was run.

## Limitations

The mock planner uses deterministic draft templates and simple text cues; it is
not a semantic fact checker, source retriever, curriculum verifier, or cultural
reviewer. `source_reference_ids` remain empty until a separately reviewed
source workflow supplies them. Cultural and content approval still require
their own review steps. No image, video, voice, subtitle, or MP4 generation and
no LoRA training were performed. This checkpoint does not claim
`PROMPT_TO_VIDEO_PASS`.
