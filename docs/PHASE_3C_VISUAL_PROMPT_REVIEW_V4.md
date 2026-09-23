# Phase 3C-C2E — Final Visual Prompt Lock Readiness Review

Status: `VISUAL_PROMPT_V4_LOCK_READINESS_REVIEW`

VisualBibleSet remains `IN_REVIEW`; cultural review remains `PENDING`. No Bible approval/lock, keyframe generation, media generation, or inference was performed.

## Base model provenance

- Registry ID: `sdxl-base-1.0`
- Source: `stabilityai/stable-diffusion-xl-base-1.0`
- Revision: `462165984030d82259a11f4367a4eed129e94a7b`
- Checkpoint: `sd_xl_base_1.0.safetensors`
- SHA-256: `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`
- Architecture: `SDXL_BASE`
- Local checkpoint hash matched registry exactly.

## CharacterBible versions

| Scope | ID | Version/state | Notes |
|---|---|---|---|
| recurring student | `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` | v2 / APPROVED | Đội viên presentation; red scarf; white short-sleeved collared shirt; dark navy trousers; simple shoes; no logo/text |
| recurring student prior | `d706102e-de1c-5207-b389-9ed573f3fd87` | v1 / APPROVED | preserved for audit |
| teacher | `c92a7bf1-39c0-5d6d-83c5-159d77a44d96` | DRAFT | modest neutral professional clothing; no student uniform/red scarf |
| community adult | `0d856b38-89a8-5780-ac25-8c97e712753c` | APPROVED | practical everyday clothing; no student uniform/red scarf |

## Teacher review checklist

- Adult teacher; supportive educational role; modest neutral clothing; no student uniform; no red scarf; no invented school logo.
- Scene 3 classroom instruction; Scene 4 outdoor supervision.
- Human approval remains outstanding.

## Background cohorts

- `background_students`: Grade 4 age band, approved uniform design, visually secondary, no persistent face identity, never recurring student ID.
- `background_community_adults`: practical everyday clothing, no student uniform/red scarf, no persistent identity, visually secondary.

## LoRA and reference-image status

- `style_lora_ids=[]`; `character_lora_ids=[]`; `lora_status=NOT_ASSIGNED`.
- `reference_status=NOT_GENERATED`; `consistency_readiness=PROMPT_ONLY`.
- This is not a final production configuration while Style LoRA is unassigned.

## V4 packages
### Scene 1 — Mở đầu: Cảnh đồng bằng Bắc Bộ (5s)
- Foreground subjects/roles: ["foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo", "foreground community adult, practical everyday clothing, no student uniform, no red scarf"]
- Background cohorts: {"background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID.", "background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary."}
- Environment: flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery
- Action: Landscape-led establishing view with small distant student and community adult figures.
- Composition: Landscape-led wide establishing composition; subjects small and distant.
- Camera: wide establishing shot
- Lighting: Soft natural daylight, bright and calm.
- Keyframe prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery | foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo; foreground community adult, practical everyday clothing, no student uniform, no red scarf | Landscape-led establishing view with small distant student and community adult figures. | Landscape-led wide establishing composition; subjects small and distant. | wide establishing shot | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water, invented school logo or signage
- Motion intent: none; intended camera motion: none; transition: none
- Model/version/hash metadata: `{"aspect_ratio": "16:9", "background_cohorts": {"background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary.", "background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID."}, "base_model_id": "sdxl-base-1.0", "base_model_revision": "462165984030d82259a11f4367a4eed129e94a7b", "base_model_sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b", "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 2}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "character_lora_ids": [], "checkpoint_filename": "sd_xl_base_1.0.safetensors", "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "55284b23-c8ac-5e9e-869f-793081873e00", "lora_status": "NOT_ASSIGNED", "model_architecture": "SDXL_BASE", "prompt_compiler_version": "structured-visual-prompt-compiler-v4", "reference_status": "NOT_GENERATED", "style_lora_ids": [], "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Package: `visual-prompt-package-v4` / `a48aaddfdcd064551411eedcabb801fce5bec51789356c5ddf46ce971c1a0e29`; keyframe hash `f3f070d00c6f9378a6a6aa5c67a2c50be977ffa9d3899caebdfefb593aa707e0`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 2 — Học sinh đến trường (5s)
- Foreground subjects/roles: ["foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo"]
- Background cohorts: {"background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID.", "background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary."}
- Environment: simple modern primary school, classroom and schoolyard with trees, no school signage text
- Action: Recurring student arrives with a reusable collection bag and one young tree seedling; optional background school peers remain visually secondary.
- Composition: Balanced composition with clear foreground action and secondary background cohort.
- Camera: medium-wide shot
- Lighting: Soft natural daylight, bright and calm.
- Keyframe prompt: Bright friendly 2D educational animation for Grade 4 learning. | simple modern primary school, classroom and schoolyard with trees, no school signage text | foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo | Recurring student arrives with a reusable collection bag and one young tree seedling; optional background school peers remain visually secondary. | Balanced composition with clear foreground action and secondary background cohort. | medium-wide shot | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water, invented school logo or signage
- Motion intent: none; intended camera motion: none; transition: none
- Model/version/hash metadata: `{"aspect_ratio": "16:9", "background_cohorts": {"background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary.", "background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID."}, "base_model_id": "sdxl-base-1.0", "base_model_revision": "462165984030d82259a11f4367a4eed129e94a7b", "base_model_sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b", "character_bible_versions": {"a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 2}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182"], "character_lora_ids": [], "checkpoint_filename": "sd_xl_base_1.0.safetensors", "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "68b8e2a3-517e-5ea2-9c3b-1d40ba9a9002", "lora_status": "NOT_ASSIGNED", "model_architecture": "SDXL_BASE", "prompt_compiler_version": "structured-visual-prompt-compiler-v4", "reference_status": "NOT_GENERATED", "style_lora_ids": [], "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Package: `visual-prompt-package-v4` / `e5ed2ef7f94bc7af80fa904becd1dd08335004ad8dbf8c5cbd10713c399986ee`; keyframe hash `58dea0d4af1b1b472389351fbe7ae1bb7ba902c7366f0bbd7bfb5256c49dc923`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 3 — Bài học về bảo vệ môi trường (5s)
- Foreground subjects/roles: ["foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo", "supportive adult teacher, modest professional neutral clothing, no student uniform, no red scarf, no invented school logo"]
- Background cohorts: {"background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID.", "background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary."}
- Environment: simple modern primary school, classroom and schoolyard with trees, no school signage text
- Action: Teacher gives a classroom lesson while recurring student and background students listen; simple symbol visual aid without words.
- Composition: Balanced composition with clear foreground action and secondary background cohort.
- Camera: medium-wide shot
- Lighting: Soft natural daylight, bright and calm.
- Keyframe prompt: Bright friendly 2D educational animation for Grade 4 learning. | simple modern primary school, classroom and schoolyard with trees, no school signage text | foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo; supportive adult teacher, modest professional neutral clothing, no student uniform, no red scarf, no invented school logo | Teacher gives a classroom lesson while recurring student and background students listen; simple symbol visual aid without words. | Balanced composition with clear foreground action and secondary background cohort. | medium-wide shot | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water, invented school logo or signage
- Motion intent: none; intended camera motion: none; transition: none
- Model/version/hash metadata: `{"aspect_ratio": "16:9", "background_cohorts": {"background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary.", "background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID."}, "base_model_id": "sdxl-base-1.0", "base_model_revision": "462165984030d82259a11f4367a4eed129e94a7b", "base_model_sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b", "character_bible_versions": {"a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 2, "c92a7bf1-39c0-5d6d-83c5-159d77a44d96": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "c92a7bf1-39c0-5d6d-83c5-159d77a44d96"], "character_lora_ids": [], "checkpoint_filename": "sd_xl_base_1.0.safetensors", "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "68b8e2a3-517e-5ea2-9c3b-1d40ba9a9002", "lora_status": "NOT_ASSIGNED", "model_architecture": "SDXL_BASE", "prompt_compiler_version": "structured-visual-prompt-compiler-v4", "reference_status": "NOT_GENERATED", "style_lora_ids": [], "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Package: `visual-prompt-package-v4` / `38dfb7c3afcbbe92a0dee23af92f73cf391d1dc930c34ad5f2d128e9b8ac00bb`; keyframe hash `0bb266a1e31db160dddbfb0de303534e0fc7f028d0882afc82267764d94c2bab`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 4 — Học sinh ra ngoài thực hành (6s)
- Foreground subjects/roles: ["foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo", "supportive adult teacher, modest professional neutral clothing, no student uniform, no red scarf, no invented school logo"]
- Background cohorts: {"background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID.", "background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary."}
- Environment: flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery
- Action: Teacher clearly supervises students collecting ordinary non-hazardous litter with protective gloves at a safe distance from the water.
- Composition: Balanced composition with clear foreground action and secondary background cohort.
- Camera: medium-wide shot
- Lighting: Soft natural daylight, bright and calm.
- Keyframe prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery | foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo; supportive adult teacher, modest professional neutral clothing, no student uniform, no red scarf, no invented school logo | Teacher clearly supervises students collecting ordinary non-hazardous litter with protective gloves at a safe distance from the water. | Balanced composition with clear foreground action and secondary background cohort. | medium-wide shot | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water, invented school logo or signage
- Motion intent: none; intended camera motion: none; transition: none
- Model/version/hash metadata: `{"aspect_ratio": "16:9", "background_cohorts": {"background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary.", "background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID."}, "base_model_id": "sdxl-base-1.0", "base_model_revision": "462165984030d82259a11f4367a4eed129e94a7b", "base_model_sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b", "character_bible_versions": {"a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 2, "c92a7bf1-39c0-5d6d-83c5-159d77a44d96": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "c92a7bf1-39c0-5d6d-83c5-159d77a44d96"], "character_lora_ids": [], "checkpoint_filename": "sd_xl_base_1.0.safetensors", "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "780190e3-0ab3-596d-979a-42ba8104a1f1", "lora_status": "NOT_ASSIGNED", "model_architecture": "SDXL_BASE", "prompt_compiler_version": "structured-visual-prompt-compiler-v4", "reference_status": "NOT_GENERATED", "style_lora_ids": [], "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Package: `visual-prompt-package-v4` / `ae09548d7f48b2c7096b1bd99b8a4854a4ce7116e5c5786602793b6192eef3ff`; keyframe hash `5e0b9956a84fa6f9e46c70228edc86cc1d3c0a9f634190963591460aa461fd76`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 5 — Người dân tham gia (6s)
- Foreground subjects/roles: ["foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo", "foreground community adult, practical everyday clothing, no student uniform, no red scarf"]
- Background cohorts: {"background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID.", "background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary."}
- Environment: flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery
- Action: Recurring student and community adult distinguishable by wardrobe while sorting ordinary litter and supporting safe planting.
- Composition: Balanced composition with clear foreground action and secondary background cohort.
- Camera: medium-wide shot
- Lighting: Soft natural daylight, bright and calm.
- Keyframe prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery | foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo; foreground community adult, practical everyday clothing, no student uniform, no red scarf | Recurring student and community adult distinguishable by wardrobe while sorting ordinary litter and supporting safe planting. | Balanced composition with clear foreground action and secondary background cohort. | medium-wide shot | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water, invented school logo or signage
- Motion intent: none; intended camera motion: none; transition: none
- Model/version/hash metadata: `{"aspect_ratio": "16:9", "background_cohorts": {"background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary.", "background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID."}, "base_model_id": "sdxl-base-1.0", "base_model_revision": "462165984030d82259a11f4367a4eed129e94a7b", "base_model_sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b", "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 2}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "character_lora_ids": [], "checkpoint_filename": "sd_xl_base_1.0.safetensors", "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "780190e3-0ab3-596d-979a-42ba8104a1f1", "lora_status": "NOT_ASSIGNED", "model_architecture": "SDXL_BASE", "prompt_compiler_version": "structured-visual-prompt-compiler-v4", "reference_status": "NOT_GENERATED", "style_lora_ids": [], "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Package: `visual-prompt-package-v4` / `7421782a40d0776ddedde1949236b5ec190207df6bc612909161b2b3481fb50a`; keyframe hash `bff5d2d2cea40de9e4297f1173c98e64bab9d49e241b7e794ac05df248bfe3cd`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 6 — Cây non được trồng (5s)
- Foreground subjects/roles: ["foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo", "foreground community adult, practical everyday clothing, no student uniform, no red scarf"]
- Background cohorts: {"background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID.", "background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary."}
- Environment: flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery
- Action: Recurring student and community adult plant one young non-specific tree with simple safe tools; the tree remains young.
- Composition: Balanced composition with clear foreground action and secondary background cohort.
- Camera: medium-wide shot
- Lighting: Soft natural daylight, bright and calm.
- Keyframe prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery | foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo; foreground community adult, practical everyday clothing, no student uniform, no red scarf | Recurring student and community adult plant one young non-specific tree with simple safe tools; the tree remains young. | Balanced composition with clear foreground action and secondary background cohort. | medium-wide shot | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water, invented school logo or signage
- Motion intent: none; intended camera motion: none; transition: none
- Model/version/hash metadata: `{"aspect_ratio": "16:9", "background_cohorts": {"background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary.", "background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID."}, "base_model_id": "sdxl-base-1.0", "base_model_revision": "462165984030d82259a11f4367a4eed129e94a7b", "base_model_sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b", "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 2}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "character_lora_ids": [], "checkpoint_filename": "sd_xl_base_1.0.safetensors", "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "780190e3-0ab3-596d-979a-42ba8104a1f1", "lora_status": "NOT_ASSIGNED", "model_architecture": "SDXL_BASE", "prompt_compiler_version": "structured-visual-prompt-compiler-v4", "reference_status": "NOT_GENERATED", "style_lora_ids": [], "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Package: `visual-prompt-package-v4` / `0c87876ce5b30d16df46e11b2cb6956d32a3abfac3c2717c1e941c6112ba8af6`; keyframe hash `7d823ca12209fd33f300a902151eebde3edaad0fcd92014be005a93dc94954a7`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 7 — Thông điệp bảo vệ thiên nhiên (8s)
- Foreground subjects/roles: ["foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo", "foreground community adult, practical everyday clothing, no student uniform, no red scarf"]
- Background cohorts: {"background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID.", "background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary."}
- Environment: flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery
- Action: Positive group result: clean riverbank, level cultivated fields and newly planted young trees.
- Composition: Wide positive group composition with clean riverbank and young trees.
- Camera: wide establishing shot
- Lighting: Soft natural daylight, bright and calm.
- Keyframe prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery | foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo; foreground community adult, practical everyday clothing, no student uniform, no red scarf | Positive group result: clean riverbank, level cultivated fields and newly planted young trees. | Wide positive group composition with clean riverbank and young trees. | wide establishing shot | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water, invented school logo or signage
- Motion intent: subtle group stillness; intended camera motion: subtle group stillness; transition: none
- Model/version/hash metadata: `{"aspect_ratio": "16:9", "background_cohorts": {"background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary.", "background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID."}, "base_model_id": "sdxl-base-1.0", "base_model_revision": "462165984030d82259a11f4367a4eed129e94a7b", "base_model_sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b", "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 2}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "character_lora_ids": [], "checkpoint_filename": "sd_xl_base_1.0.safetensors", "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "55284b23-c8ac-5e9e-869f-793081873e00", "lora_status": "NOT_ASSIGNED", "model_architecture": "SDXL_BASE", "prompt_compiler_version": "structured-visual-prompt-compiler-v4", "reference_status": "NOT_GENERATED", "style_lora_ids": [], "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Package: `visual-prompt-package-v4` / `e0c6c951f302bceba8964ce6c8b7f28c780a16e8d5002ba096edaab35b5b56c7`; keyframe hash `73fb54100992b871189a186895a3388c49242f212db9744483f38443b92905fa`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 8 — Kết thúc (5s)
- Foreground subjects/roles: ["foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo", "foreground community adult, practical everyday clothing, no student uniform, no red scarf"]
- Background cohorts: {"background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID.", "background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary."}
- Environment: flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery
- Action: Calm closing landscape with small distant figures waving.
- Composition: Calm panoramic closing composition with small distant figures.
- Camera: wide establishing shot
- Lighting: Soft natural daylight, bright and calm.
- Keyframe prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery | foreground recurring student, age 8–10, friendly neutral face, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, no logo; foreground community adult, practical everyday clothing, no student uniform, no red scarf | Calm closing landscape with small distant figures waving. | Calm panoramic closing composition with small distant figures. | wide establishing shot | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water, invented school logo or signage
- Motion intent: gentle pull-back; intended camera motion: gentle pull-back; transition: slow fade-out
- Model/version/hash metadata: `{"aspect_ratio": "16:9", "background_cohorts": {"background_community_adults": "Practical everyday clothing, no student uniform, no red scarf, no persistent identity, visually secondary.", "background_students": "Grade 4 age band, same approved school uniform design, no persistent face identity, visually secondary, never a recurring student ID."}, "base_model_id": "sdxl-base-1.0", "base_model_revision": "462165984030d82259a11f4367a4eed129e94a7b", "base_model_sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b", "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 2}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "character_lora_ids": [], "checkpoint_filename": "sd_xl_base_1.0.safetensors", "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "55284b23-c8ac-5e9e-869f-793081873e00", "lora_status": "NOT_ASSIGNED", "model_architecture": "SDXL_BASE", "prompt_compiler_version": "structured-visual-prompt-compiler-v4", "reference_status": "NOT_GENERATED", "style_lora_ids": [], "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Package: `visual-prompt-package-v4` / `81371006672d02c37df3061acc191900553194560cc1cd629b718d5e3aba2942`; keyframe hash `ac8daa45be905a2c97e40ec9908b67afe804448259393eafcd46129efaae026b`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

## Validation gates

- Package counts: v1 SUPERSEDED = 8; v2 SUPERSEDED = 8; v3 SUPERSEDED = 8; v4 ACTIVE = 8. All prior rows preserved.
- Model-facing prompt scan: no UUID, hash, `flat_delta`, `reference_status`, `PROMPT_ONLY`, `NOT_GENERATED`, `WIDE`, `MEDIUM_WIDE`, or internal reference phrases.
- Scene 7 and Scene 8 use different keyframe prompts, keyframe hashes, actions and compositions.
- Scene 4 includes adult supervision, gloves, safe distance from water, ordinary non-hazardous litter, and no students in water.
- Teacher remains DRAFT; cultural review remains PENDING; VisualBibleSet remains IN_REVIEW.
- No `CHARACTER_CONSISTENCY_PASS`, `CULTURAL_APPROVED`, `VISUAL_BIBLE_APPROVED`, `KEYFRAME_PASS`, or `PROMPT_TO_VIDEO_PASS` is claimed.
