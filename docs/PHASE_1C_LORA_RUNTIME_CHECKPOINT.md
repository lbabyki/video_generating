# Phase 1C-A — Controlled SDXL LoRA Runtime

Status: **RUNTIME_READY**, not `LORA_INFERENCE_PASS`.

Built-in `LoraLoader` support is implemented for an ordered maximum of two
LoRAs: one STYLE plus optionally one ENVIRONMENT or CHARACTER. Validation
requires an existing `.safetensors` file, matching SHA-256, `SDXL_BASE`,
complete license provenance, `APPROVED` status, and strengths inside manifest
bounds. MOTION, DRAFT, TESTING, BLOCKED, DEPRECATED, wrong base, missing files,
and hash mismatches are rejected.

Variant B has no `LoraLoader`. Variant C chains built-in `LoraLoader` nodes in
declared order but cannot be submitted by this scope: no LoRA was downloaded,
registered, or inferred. Snapshots lock base and LoRA provenance, order,
strengths, trigger words, prompt, seed and workflow hash; governance remains
`DRAFT` and release eligibility false.
