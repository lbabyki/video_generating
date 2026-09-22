# Phase 3B — Local Qwen Prompt Planner

Status: **NOT_READY**. The local Ollama provider, persistence, resource guard,
and mocked integration coverage are in place. Two authorized live golden
compilations failed validation, each after one repair. Phase 3B does not pass
the live golden-output gate.

## Scope and API

Phase 3A's `PromptPlanner`, request and plan schema, and compilation service
were extended. `PROMPT_PLANNER_PROVIDER=mock|ollama` selects the provider from
server configuration; request payloads cannot select a URL or model. The API
remains compatible and reports provider, requested model, resolved digest,
prompt-template version, status, warnings, errors, repair count, and resource
metrics. Failed compilations persist with `COMPILATION_FAILED` and a null
`plan_json`; they cannot be validated as successful or approved.

Ollama structured output passes `ProjectPlan.model_json_schema()` directly to
`/api/generate`. The final response must be a JSON object with no Markdown or
surrounding prose. The system instruction treats delimited prompt text as data,
disables thinking, forbids invented sources and approvals, and requires exact
duration constraints. Pydantic and deterministic validators check every plan.
At most one structured repair is attempted. Prompts, model responses, tokens,
and hidden reasoning are not written to application logs or failure records.

Configuration is read from environment: `PROMPT_PLANNER_PROVIDER`,
`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`,
`OLLAMA_KEEP_ALIVE`, `PROMPT_PLANNER_TEMPERATURE`, `PROMPT_PLANNER_SEED`,
`PROMPT_TEMPLATE_VERSION`, `PROMPT_PLANNER_ALLOW_REMOTE`, and the GPU idle
threshold variables. Ollama defaults to loopback and remote URLs are rejected
unless an administrator explicitly opts in. The generation call uses structured
JSON Schema, `think=false`, bounded timeout/response size, temperature and seed.

Before inference, the guard checks Ollama's active model list, Docker runtimes,
training processes, GPU utilization, and VRAM. It never kills a process. After
an attempted generation it requests `keep_alive=0`, verifies `ollama ps`, and
records before/peak/after VRAM. If unload or VRAM release is not verified, the
compilation fails closed.

## Model provenance

The model was already installed locally, so no `ollama pull` was run. Read-only
local Ollama metadata reported:

- Ollama: **0.32.6**, health endpoint passed.
- Requested tag: `qwen3:14b`.
- Resolved digest: `bdbd181c33f2ed1b31c972991882db3cf4d192569092138a7d29e973cd9debe8`.
- Architecture/family: `qwen3`; parameter size: `14.8B`.
- Quantization: `Q4_K_M`; installed size: **9,276,198,565 bytes**.
- License recorded: **Apache-2.0**.
- Ollama `modified_at` used as the installed timestamp:
  `2026-09-22T16:36:48.051680983+07:00`.

The failed live compilation stored this provenance with template
`phase3b-v1`. A follow-up prompt fix is versioned `phase3b-v2`, so its request
hash will not collide with the failed v1 attempt. Resolved model digest,
provider, and template version participate in request hashing; the mutable
tag alone is insufficient.

Migration `0008_qwen_planner_provenance` follows `0007_prompt_compilations`.
It adds compilation status and planner metadata, makes plan JSON nullable for
failed runs, and stores local model provenance. Both the clean SQLite upgrade
and the existing local database are at **0008_qwen_planner_provenance**.

## Tests and checks

- Full pytest: **65 passed**, one upstream Starlette deprecation warning.
- Mocked Ollama HTTP tests cover structured schema, invalid JSON, schema and
  extra-field failures, one repair and failed repair, timeout, connection error,
  oversized response, local URL enforcement, digest-sensitive idempotency,
  prompt-injection delimiters, invented sources, grounding, governance,
  explicit-scene order, busy-resource refusal, unload, and hidden-reasoning
  omission.
- API create/get/validate/approve smoke with the configured mock provider:
  **PASS** (FastAPI TestClient).
- Clean Alembic upgrade/current and existing database upgrade: **PASS**,
  migration head `0008_qwen_planner_provenance`.
- Application SQLite foreign keys: **enabled**.
- `docker compose config --quiet`: **PASS**.
- ComfyUI regression smoke after Qwen unload: **PASS**, localhost-only and
  CUDA/NVIDIA visible. ComfyUI was stopped afterward; it was stopped before
  the smoke.

## Single golden live attempt

The Phase 3A golden request was submitted once through the API after tests
passed and read-only preflight reported Ollama idle, ComfyUI/training inactive,
GPU at 9% and 984 MiB used, and 47 GiB free disk space. The installed model was
used without pulling another copy. The API performed one generation and one
structured repair.

The final response still violated the scene duration maximum: four scenes had
`duration_seconds > 8`. The service stored status `COMPILATION_FAILED`, one
repair attempt, filtered validation errors, and **no partial ProjectPlan**.
This means there is no valid live scene count or total duration to report.
Generation latency was not included in the failure response; observed command
wall time was approximately 31 seconds.

VRAM was **1,023 MiB before**, **30,691 MiB peak**, and **994 MiB after**. Ollama
reported no loaded models after the `keep_alive=0` unload; VRAM release
verification passed. ComfyUI smoke ran only after this unload.

The failure showed that the total-duration invariant was not explicit in the
v1 system instruction and that repair feedback omitted numeric schema bounds.
The code now uses `phase3b-v2`, explicitly instructs 3–8 seconds per scene and
the requested total, and includes safe limit values in repair errors. These
changes pass mocked tests but were not sent to Qwen because the task limited
this run to one live compilation.

## Limitations

The golden live plans did not validate, so this checkpoint does not claim
`QWEN_PROMPT_PLANNER_READY` or `PROMPT_TO_VIDEO_PASS`. No image, video, audio,
subtitle, keyframe, or LoRA inference/training was performed; only local
text-planner inference was attempted. No model blob was added to Git, and
nothing was committed or pushed.

## Second authorized golden live attempt — phase3b-v2

On 2026-09-22, one additional API compilation was made using the existing
Phase 3A golden request and `phase3b-v2`. Preflight confirmed Ollama 0.32.6,
`qwen3:14b`, digest
`bdbd181c33f2ed1b31c972991882db3cf4d192569092138a7d29e973cd9debe8`,
Q4_K_M, Apache-2.0, temperature 0, seed 314159, and `keep_alive=0`. ComfyUI,
training workers, and loaded Ollama models were absent. VRAM was 987 MiB before
generation.

Compilation `7e9977ae-ac24-438f-bcd9-fd00e8f8011f` ended as
`COMPILATION_FAILED` after exactly one repair. The database retains the failed
record with no `plan_json`, seed, temperature, 54,695 ms latency, request hash,
template, model digest, validation result, and resource measurements. Its
validation error is recorded as `(): value_error`, a root-level Pydantic model
validation error. This version of the validator did not preserve the root
error message or a field/scene location, so the failed record cannot identify
the specific violated plan invariant. No scene durations or total can be
reported because no plan was persisted. This error is reported as stored; it
has not been inferred or replaced with another validation outcome.

The original v1 failed record remains unchanged. Ollama was empty after the
attempt; VRAM peak was 30,683 MiB and post-unload VRAM was 984 MiB. The attempt
did not satisfy the live gate. The full post-run suite passed (65 tests),
Alembic current is `0009_qwen_run_metrics`, and Docker Compose configuration
validation passed. There was no third live attempt.
