# Phase 3D-B — BI Mascot Asset Intake and VisualBible v2 Foundation

Status: `MASCOT_ASSET_REGISTRY_READY_FOR_HUMAN_REVIEW`

- Approved VisualBibleSet v1: `9f2272dd-2237-53ed-a3aa-fd570e89a75e` (unchanged, APPROVED)
- VisualBibleSet v2: `6d9297b4-b762-5b2c-90b1-54fd144592b5` (DRAFT)
- Mascot CharacterBible: `a837d46e-29d0-5857-a6f2-1818d066f678` (DRAFT, PENDING review)

## Asset registry

| Asset ID | Canonical filename | Source filename | SHA-256 | Expression/orientation | Props | Alpha | Permission | Review |
|---|---|---|---|---|---|---|---|---|
| `215ccf9f-d104-56bd-b963-b72f8151c7d7` | `BACK_THREE_QUARTER.png` | `BACKSIDE.png` | `db263d335674ea886a8d2e16338a45386d5930543f925a6e869ad0c990d8dff2` | orientation reference | [] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |
| `a76c57c7-a51f-5bf0-b751-5083e8d3bff7` | `CRYING.png` | `CRYING.png` | `f223df85dfdd200c01c516f6ecc9d59a507a519592309c9de364d63bede0b83e` | sad/crying | [] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |
| `3b7f57fb-e219-57f2-97ee-e035090cc002` | `DETERMINED.png` | `DETERMINEDSTUDY.png` | `6e8fa599bc3b5d58051805dd5e1f9c325cbe8615f580d1fef7e1c63cc2cadbca` | determination | [] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |
| `94ea16e5-b533-5e3c-b173-d0ff7447d28d` | `FRIENDLY_SMILE.png` | `FRIENDLYSMILE.png` | `a94a26ee6c959b3c530fcfbc8b8ae2cec199a8128caf84c009eddecc3c825fc6` | friendly positive response | [] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |
| `d63f1dec-1c7e-53aa-a5cd-e52b4522a26a` | `GREETING.png` | `GREETING.png` | `94402e948108f7fff2e554c24e4c46380f816336e10c51e0a389582d536cfd83` | introduction and closing greeting | [] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |
| `92f44c29-b280-522c-8b2d-291e39ed7c86` | `SCARED.png` | `SCARED.png` | `b9a8e4b7430e79e14791037092137bf6a3818e02caccca9c572a28727b92ea73` | immediate fear/startle | [] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |
| `5bf33163-884a-584b-9070-6e7a4f09f927` | `STUDYING_SIDE.png` | `STUDYINGSIDE.png` | `4101ccb4fd4693b206573c52e57217cc86dd637be20da23ee75a5b1d4466a510` | studying activity from side/rear angle | ["desk", "chair", "book", "pencil"] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |
| `1b79e515-484a-5900-88e2-099de4f48aa8` | `TIRED.png` | `TIRED.png` | `cbec1cc875430cbc5aa161c89d7953e718d18d7ba873d0ec410eeefcf6ffad67` | tired/low-energy response | [] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |
| `d6af7c84-cbbd-5d40-8d95-802d8773fbc4` | `WORRIED.png` | `WORRIED.png` | `d229daa854be7cc7582c988c2e629005b60336010d76d6729994998ab477736c` | concern about an environmental problem | [] | True | reference=REFERENCE_ONLY; training=PENDING | PENDING |

## Mascot CharacterBible

- provisional name: BI; type: NON_HUMAN_EDUCATIONAL_MASCOT; role: recurring educational guide; runtime: OVERLAY_EDUCATIONAL_GUIDE.
- Identity: rounded green body, red baseball-style cap, large brown eyes, short green arms/legs, simple silhouette.
- Red cap is required in every approved state. No human clothing, school uniform, red scarf, logo, text or watermark.
- BI is not a Vietnamese student and does not replace factual human roles.
- Governance: DRAFT; release_eligible=false; review_status=PENDING.

## Warnings and permissions

- `STUDYING_SIDE.png` has desk/chair/book/pencil props and `prop_contamination=true`; exclude from identity-only training by default.
- FRIENDLY_SMILE and GREETING are related positive/waving states with different expression intensity.
- SCARED and WORRIED have similar hand placement but different emotional intensity.
- BACK_THREE_QUARTER is not a true direct-back view; the set lacks a neutral front view.
- Creation tool/model and ownership are UNKNOWN; all assets are REFERENCE_ONLY and `training_permission=PENDING`.
- Nine assets support runtime expression selection but do not establish LoRA training readiness.

## Candidate 001

- Candidate ID: `8c96c167-8f2f-58b0-863e-6f8a111cd5cc`
- human_review_status: `REJECTED`
- reference_status: `REJECTED`
- release_eligible: `false`
- Audit reason: fixed recurring student strategy replaced by mascot continuity strategy.
- Candidate 002 was not created.

## Verification

- All nine files were resolved under the mascot data root; traversal/symlink escape was not used.
- PNG magic, 500×500 dimensions, RGBA mode and alpha channel were verified; expected hashes matched exactly.
- No source image was modified, renamed, copied into the repository, or Git-tracked.
- No Qwen, ComfyUI, SDXL, LoRA, IP-Adapter, ControlNet, training or media generation ran.
- VisualBibleSet v1, ProjectPlan, compilation provenance and v1–v4 prompt packages were unchanged.
- Full pytest: 133 passed; Alembic `0019_mascot_assets (head)`; FK check clean; API smoke 200; Compose and diff checks passed.

## Human review update

- Reviewer `40a6df62-f60a-439c-8509-890b9db2ee08` (`PROJECT_OWNER`, `ACTIVE`) recorded `APPROVED_WITH_RESTRICTIONS` for Mascot CharacterBible `a837d46e-29d0-5857-a6f2-1818d066f678` and all nine runtime assets.
- Assets are approved for reference/runtime use only; `training_permission=PENDING` remains unchanged for every asset.
- BI remains a `NON_HUMAN_EDUCATIONAL_MASCOT` overlay guide and must not replace student, teacher or community roles or obscure subtitles, faces, activities or cultural evidence.
- `STUDYING_SIDE` remains excluded from identity-only training; `BACK_THREE_QUARTER` is not direct-back.
- VisualBibleSet v2 remains `DRAFT`. No v5 prompt packages were created and no dataset/training/LoRA approval was granted.
