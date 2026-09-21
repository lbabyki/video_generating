# Phase 1C experiment 001 — Cultural Prompt Control

Status: **EXPERIMENT RECORDED; Phase 1C remains open.** Technical result is
`PASS`; the subsequent human-assisted cultural review is `REJECTED` and the
experiment is not release eligible. See
`docs/PHASE_1C_EXPERIMENT_001_CULTURAL_REVIEW.md`.

| Field | Value |
| --- | --- |
| Phase / experiment / variant | `PHASE_1C` / `CULTURAL_PROMPT_CONTROL` / `B_BASE_NO_LORA` |
| Governance status | `DRAFT` |
| Change reason | `CULTURAL_PROMPT_CORRECTION` |
| Parent Phase 1B SHA-256 | `ab0dd786fd51c4f05510124e08c9275d4d68a02a00c774e7e2522ea27798c076` (rechecked unchanged) |
| Model / revision / SHA-256 | SDXL Base 1.0 / `462165984030d82259a11f4367a4eed129e94a7b` / `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b` |
| ComfyUI revision | `b0f4b7b294ce482a2e071d9d762c133d38c7aa07` |
| Workflow SHA-256 | `6d6cefd2e3233c99644441e652dd8d9775df4aa88bb177171ebda8bd810d5e20` |
| Sampling | seed `20260921`; `euler` / `normal`; 25 steps; CFG 6.5; 1344×768; batch 1 |
| Output / SHA-256 | `output/phase1c/experiment-001/variant-b-base-no-lora_00001_.png` / `3da46fd8ec0f07985e7d38e7484d567cfca3791dff7c5c65903c6d92b988ea03` |
| Inference | 3.080s client-side; ComfyUI log reports 2.63s |
| VRAM | 8360 MiB before; 8712 MiB peak observed; 8356 MiB after, of 32607 MiB |

The workflow retained all Phase 1B model and sampler parameters. Only the
positive and negative prompts changed to the specified Northern Vietnamese
Red River Delta cultural description. It uses only built-in nodes and no LoRA,
ControlNet, IP-Adapter, or third-party custom node.

Actual verification: `33 passed` in pytest; ComfyUI health smoke passed;
Pillow confirmed `PNG (1344, 768)`; the experiment PNG and metadata sidecar
are Git-ignored. No approval, release, commit, or push was performed.

Variant B is preserved as the no-LoRA control image. It must not be regenerated
or overwritten; controlled LoRA integration is a separate subsequent scope.
