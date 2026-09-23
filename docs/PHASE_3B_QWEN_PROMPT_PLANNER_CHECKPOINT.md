# Phase 3B — Local Qwen Prompt Planner

Status: **QWEN_PROMPT_PLANNER_READY**. Phase 3B-R3 terrain resolution passed
one authorized live golden compilation with `phase3b-v5`. This checkpoint is
not a `PROMPT_TO_VIDEO_PASS`; all four historical failed records are preserved.

## Scope and API

Phase 3A's `PromptPlanner`, request and plan schema, and compilation service
were extended. `PROMPT_PLANNER_PROVIDER=mock|ollama` selects the provider from
server configuration; request payloads cannot select a URL or model. The API
remains compatible and reports provider, requested model, resolved digest,
prompt-template version, status, warnings, errors, repair count, and resource
metrics. Failed compilations persist with `COMPILATION_FAILED` and a null
`plan_json`; they cannot be validated as successful or approved.

Ollama structured output passes `PlannerCandidate.model_json_schema()` to
`/api/generate`. The compiler validates candidate semantics, resolves stable
IDs, allocates integer durations, and constructs the final `ProjectPlan` in
`DRAFT`. The model does not supply final IDs, source references, keyframes, or
release decisions. At most one repair is used for candidate JSON/schema or
semantic reference errors; timeline allocation never invokes a repair.
Structured validation errors and the candidate response hash are persisted.
Optional local diagnostics store only sanitized parseable candidate JSON under
the ignored diagnostics directory with restrictive file permissions; paths
and content are excluded from normal API responses. Model thinking is not
persisted.

Configuration is read from environment: `PROMPT_PLANNER_PROVIDER`,
`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`,
`OLLAMA_KEEP_ALIVE`, `PROMPT_PLANNER_TEMPERATURE`, `PROMPT_PLANNER_SEED`,
`PROMPT_TEMPLATE_VERSION`, `PROMPT_PLANNER_STORE_DIAGNOSTICS`,
`PROMPT_PLANNER_DIAGNOSTICS_DIR`, `PROMPT_PLANNER_ALLOW_REMOTE`, and the GPU
idle threshold variables. Ollama defaults to loopback and remote URLs are rejected
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

The two historical failed live compilations used templates `phase3b-v1` and
`phase3b-v2`. The current candidate prompt is `phase3b-v3`. Resolved model
digest, provider, template, seed, temperature, and timeline allocator version
participate in request hashing; the mutable tag alone is insufficient.

Migration `0010_candidate_timeline_observability` follows `0009_qwen_run_metrics`.
It adds validation stage, error count, failed scene orders, candidate-response
SHA-256, private diagnostic path, and timeline provenance. Migrations 0008 and
0009 were not modified. The timeline record retains each suggested duration,
final integer duration, adjustment flag/reason, and allocator version.

## Tests and checks

- Full pytest: see the v3 verification section below.
- Mocked Ollama HTTP tests cover structured schema, invalid JSON, schema and
  extra-field failures, one repair and failed repair, timeout, connection error,
  oversized response, local URL enforcement, digest-sensitive idempotency,
  prompt-injection delimiters, invented sources, grounding, governance,
  explicit-scene order, busy-resource refusal, unload, and hidden-reasoning
  omission.
- API create/get/validate/approve smoke with the configured mock provider:
  **PASS** (FastAPI TestClient).
- Clean Alembic upgrade/current and existing database upgrade: recorded below,
  migration head `0010_candidate_timeline_observability`.
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

The v1 failure showed that duration limits were not enforced effectively. The
v2 live attempt also failed at a root-level Pydantic validation error whose
message was not retained. The v3 compiler separates semantic planning from
timeline arithmetic, so duration sums are produced and verified locally.

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

## Candidate compiler and v3 verification

`PlannerCandidate` contains semantic character/environment references and
scene content. Candidate validation produces structured `loc`, `type`, `msg`,
and safe context fields. Unknown character or environment references fail
semantic validation rather than inventing identities. UUID5 IDs are resolved
from the normalized request identity plus semantic entity keys, and scene IDs
from that identity, order, and title.

`DeterministicTimelineAllocator` version `largest-remainder-v1` assigns a
3-second base, distributes remaining seconds by model weights (or suggestions,
or evenly when absent), caps at 8 seconds, then assigns remainder seconds by
descending fractional remainder and scene order. It rejects scene counts
outside 7–10 and infeasible target durations. Final scene durations are
integers and total exactly the request target. This adjustment is explicit in
the persisted timeline provenance.

Verification for this implementation: full pytest **85 passed**; clean and
existing Alembic databases reached `0010_candidate_timeline_observability`;
SQLite foreign-key check, Docker Compose configuration, mock-provider API
smoke, and `git diff --check` passed. No Qwen live, ComfyUI, SDXL, LoRA, video,
TTS, or subtitle inference was run.

## Phase 3B-R2 offline semantic environment model

`RegionalEnvironmentProfile` represents the canonical region once per plan.
`SceneLocation` represents a specific place such as a rice field, riverbank,
village lane, communal-house yard, school yard, bamboo hedge, or residential
area. Each location carries the same regional profile ID while its own UUID5
location ID may differ. Scene `environment_id` values now resolve to these
location IDs; no model-provided ID is trusted.

When the request explicitly names Đồng bằng Bắc Bộ, Đồng bằng sông Hồng, or
Red River Delta, the compiler inherits canonical `red-river-delta` for scenes
that omit regional text. Equivalent aliases normalize to the same key. The
provenance records proposed text, canonical key, inheritance, alias
normalization, conflict, review state, profile ID, and normalization rule
version. Broad text such as Vietnam alone does not infer the delta.

Explicit high mountains, mountain valleys, stilt-house villages, Tây Bắc,
Tây Nguyên, or Chinese/Japanese palace architecture are rejected as regional
conflicts. Ambiguous or unsupported regional claims remain `NEEDS_REVIEW`.
Compatible scene locations do not trigger semantic repair.

Template default is now `phase3b-v4`; it was not sent to Qwen. Offline fixtures
were added under `fixtures/phase3b_r2/` for compatible locations, aliases,
request inheritance, and conflicts. No live IDs, timestamps, latency, VRAM,
or model response hashes appear in those fixtures.

R2 verification: full pytest **93 passed**, clean and existing Alembic current
remain `0010_candidate_timeline_observability`, SQLite foreign-key checks are
clean, mock-provider API smoke passed, Docker Compose configuration passed,
and `git diff --check` passed. The three historical failed compilation rows
were read-only compared before and after verification; status, hashes, metrics,
errors, and `updated_at` were unchanged. No Qwen live, ComfyUI, SDXL, LoRA,
video, TTS, or subtitle inference was run.

## Third authorized golden live compilation — phase3b-v3

On 2026-09-23, exactly one new compilation used the Lesson 08 golden request
with the `PlannerCandidate` structured schema and `phase3b-v3`. Preflight
confirmed `qwen3:14b`, digest
`bdbd181c33f2ed1b31c972991882db3cf4d192569092138a7d29e973cd9debe8`, Q4_K_M,
Apache-2.0, temperature 0, seed 314159, and `keep_alive=0`. `ollama ps` was
empty, ComfyUI was absent, no LoRA trainer or GPU training worker was active,
and VRAM was 1308 MiB before inference.

Compilation `5b204f46-21c5-4206-9c8b-c08c2eb66383` ended as
`COMPILATION_FAILED` after one candidate repair. The persisted record contains
no `plan_json`, `validation_stage=semantic_validation`, `error_count=1`,
`failed_scene_orders=[1,2,3,4,5,6,7]`, and candidate response SHA-256
`8ec926a9072489b62604b10e81f5b215a56acec247a8c6232ad5da0730eac03d`.

The exact validation error is:

```json
{
  "loc": ["environments"],
  "type": "red_river_delta_environment_required",
  "msg": "Use one shared Northern Vietnam / Red River Delta environment for every scene."
}
```

The candidate did not reach timeline allocation, so no duration provenance or
partial final plan was persisted. Inference latency was 34,641 ms. Resource
metrics were 1,303 MiB before, 31,144 MiB peak, and 1,292 MiB after unload;
`unload_verified` and `vram_released` were true. `ollama ps` was empty after
inference. The v1 and v2 failed rows remain unchanged. No fourth live attempt
was made.

## Phase 3B-R3 live golden compilation — phase3b-v5

Exactly one live compilation ran on 2026-09-23 using the Lesson 08 request.
Preflight confirmed empty `ollama ps`, no ComfyUI or training workers, and the
locked Qwen provenance: `qwen3:14b`, digest
`bdbd181c33f2ed1b31c972991882db3cf4d192569092138a7d29e973cd9debe8`, Q4_K_M,
Apache-2.0, temperature 0, seed 314159, and `keep_alive=0`. Diagnostic storage
was enabled locally with the existing Git-ignored, 0600 policy; no repair was
needed and no thinking/reasoning was stored.

Compilation `88e6c89b-8924-4661-b7ec-c3d73cc9d4ba` **SUCCEEDED** with one
initial model call and zero repairs. The plan has eight scenes and total
duration 45 seconds:

| # | Title | Location | Final duration |
|---:|---|---|---:|
| 1 | Mở đầu: Cảnh đồng bằng Bắc Bộ | Ruộng lúa Đồng bằng Bắc Bộ | 5s |
| 2 | Học sinh đến trường | Trường học | 5s |
| 3 | Bài học về bảo vệ môi trường | Trường học | 5s |
| 4 | Học sinh ra ngoài thực hành | Bờ sông | 6s |
| 5 | Người dân tham gia | Bờ sông | 6s |
| 6 | Cây non được trồng | Bờ sông | 5s |
| 7 | Thông điệp bảo vệ thiên nhiên | Ruộng lúa Đồng bằng Bắc Bộ | 8s |
| 8 | Kết thúc | Ruộng lúa Đồng bằng Bắc Bộ | 5s |

The regional profile is `red-river-delta`, terrain `flat_delta`, with profile
ID `ff0c1615-3aac-5901-94df-6a00ca731063`. All locations share that profile.
Location IDs are deterministic UUID5 values: rice field
`55284b23-c8ac-5e9e-869f-793081873e00`, riverbank
`780190e3-0ab3-596d-979a-42ba8104a1f1`, and school
`68b8e2a3-517e-5ea2-9c3b-1d40ba9a9002`. Persisted terrain provenance uses
`terrain-normalization-v1`; each model proposal resolved to `flat_delta` from
the regional profile with no conflict. Timeline provenance uses
`largest-remainder-v1`; suggested/final durations and adjustment reasons are
persisted, including 4→5, 10→8, and 4→5 second adjustments.

Governance is `DRAFT`, `release_eligible=false`, grounding is `PENDING`, and
there are no keyframes, media outputs, or source references. Character IDs and
environment/location IDs are deterministic UUID5 values and are reused
consistently across scenes. Inference latency was 17,645 ms; VRAM was 1,399 MiB
before, 31,140 MiB peak, and 1,447 MiB after unload. Unload and VRAM release
were verified. Post-run `ollama ps` was empty. The four historical failed rows
remain unchanged. This is `QWEN_PROMPT_PLANNER_READY`, not
`PROMPT_TO_VIDEO_PASS`.

## Phase 3B-R2 authorized golden live compilation — phase3b-v4

On 2026-09-23, exactly one new live compilation used the Lesson 08 golden
request with template `phase3b-v4`. Preflight confirmed an empty `ollama ps`,
no ComfyUI, LoRA trainer, or GPU worker, and the exact `qwen3:14b` model
provenance: digest `bdbd181c33f2ed1b31c972991882db3cf4d192569092138a7d29e973cd9debe8`,
Q4_K_M, Apache-2.0. Temperature was 0, seed 314159, and `keep_alive=0`.
Local diagnostic storage was enabled; its output is Git-ignored, mode 0600,
7,174 bytes, and contains only filtered candidate content (no
thinking/reasoning).

Compilation `bf048455-a69e-40df-a9db-091acbd18f93` ended as
`COMPILATION_FAILED` after exactly two model calls: one initial call and one
semantic repair. No partial `plan_json` was persisted. The final candidate had
10 scenes, but semantic validation stopped before timeline allocation. The
three exact errors were:

```json
[
  {"loc":["environments","Ruộng lúa Đồng bằng Bắc Bộ","terrain"],"type":"terrain_not_flat","msg":"Red River Delta terrain must be flat alluvial plain."},
  {"loc":["environments","Bờ sông","terrain"],"type":"terrain_not_flat","msg":"Red River Delta terrain must be flat alluvial plain."},
  {"loc":["environments","Vườn cây cộng đồng","terrain"],"type":"terrain_not_flat","msg":"Red River Delta terrain must be flat alluvial plain."}
]
```

The persisted failure records `validation_stage=semantic_validation`,
`error_count=3`, `failed_scene_orders=[1,2,3,4,5,6,7,8,9,10]`, candidate
response SHA-256
`79323d569a89e1337d92d865991307bfbe7543decc055b11237925857d0a510a`, and
empty timeline provenance. Inference latency was 41,272 ms. VRAM was 1,367 MiB
before, 31,055 MiB peak, and 1,375 MiB after unload; unload and release were
verified. `ollama ps` was empty afterward. The v1, v2, and v3 failed rows were
read-only compared and remain unchanged. No additional live compilation was
made. The checkpoint therefore remains
`RUNTIME_READY_FOR_LIVE_RETEST_R2_WITH_FAILURE`; it does not claim
`QWEN_PROMPT_PLANNER_READY` and is not a `PROMPT_TO_VIDEO_PASS`.

## Phase 3B-R3 terrain resolution

No Qwen, ComfyUI, SDXL, LoRA, video, TTS, or subtitle inference was run.
The existing diagnostic for compilation
`bf048455-a69e-40df-a9db-091acbd18f93` was analyzed as filtered candidate JSON
only. The raw terrain proposals were:

| Environment | Raw terrain | Classification | Resolution |
|---|---|---|---|
| Ruộng lúa Đồng bằng Bắc Bộ | `Đồng bằng phẳng, có dòng sông lớn chảy qua` | `COMPATIBLE` | `flat_delta` from regional profile |
| Bờ sông | `Bờ sông bằng phẳng, có cây cối ven bờ` | `LOCATION_OR_LAND_USE` | `flat_delta` inherited; field misclassified |
| Vườn cây cộng đồng | `Đất bằng phẳng, có nhiều cây xanh` | `COMPATIBLE` | `flat_delta` from regional profile |

`TerrainResolver` version `terrain-normalization-v1` now treats the regional
profile as the final terrain authority. Compatible aliases normalize to
`flat_delta`; location or land-use values inherit the profile and are marked
`model_field_misclassified`; missing values inherit without repair; ambiguous
non-conflicting values inherit with `review_required=true`; explicit mountain,
highland, plateau, Tây Bắc, or Tây Nguyên values remain conflicts and are
rejected. Each environment receives sanitized terrain provenance containing the
raw proposal, classification, resolved terrain, resolution source, inheritance,
misclassification, rule version, conflict, and review flags.

The new template is `phase3b-v5`. Its instruction places location terms in the
location field, requests `flat_delta`, forbids model UUIDs, and preserves
`PENDING`/`NEEDS_REVIEW` governance. A minimal regression fixture is stored at
`fixtures/phase3b_r3/terrain_resolution_regression.json`; it contains only the
three environment names and terrain values and no prompt, IDs, timestamps,
hashes, paths, or reasoning.

R3 verification: full pytest **122 passed**, mock-provider API tests passed,
Alembic clean/current reached `0010_candidate_timeline_observability`, SQLite
foreign-key checks are clean, Docker Compose configuration passed, and
`git diff --check` passed. The four failed compilation rows were read-only
compared and remain unchanged. No migration was required and no commit or push
was made.
