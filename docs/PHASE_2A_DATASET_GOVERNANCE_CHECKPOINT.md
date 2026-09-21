# Phase 2A — LoRA Dataset Governance

Status: **RUNTIME_READY; both datasets are EMPTY.** No images were downloaded,
scraped, generated, or exported for training.

Declared immutable-version manifests: `edu-vietnam-2d-v1` (STYLE,
`eduvn2dstyle`) and `red-river-delta-environment-v1` (ENVIRONMENT,
`redriverdeltaenv`). Assets follow QUARANTINED → VALIDATED →
CULTURAL_REVIEWED → APPROVED, with REJECTED/BLOCKED exits. Only APPROVED assets
with provenance, ML-training permission and permitted legal status may export.

Validation rejects traversal, non-PNG/JPEG/WebP, corruption, undersized files,
missing provenance, blocked license/training permission, duplicates and split
leakage. Cultural labels are reviewer-gated and do not constitute absolute
cultural evidence. Dataset images, thumbnails and exports remain Git-ignored.
