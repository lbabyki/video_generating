# Phase 3C-C2D — Visual Prompt Semantic QA and Role Scoping

Status: `VISUAL_PROMPT_V3_READY_FOR_HUMAN_REVIEW`

VisualBibleSet remains `IN_REVIEW`. Cultural review remains `PENDING`; no Bible approval, keyframe, media output, or inference was performed.

## CharacterBible audit

| Character ID | Semantic key | Display name | Role | Age band | Recurring/background | Wardrobe | Scene bindings |
|---|---|---|---|---|---|---|---|
| `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` | `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` | Học sinh lớp 4 | Tham gia hoạt động bảo vệ môi trường | 8–10 tuổi | recurring student | Áo trắng, quần xanh, giày thể thao | a0cb44fd-d264-5076-b0d9-cb525469c082, cc77b771-374c-52d9-bf62-53b1f4d58064, 1a443f2c-c582-541f-9d9b-5d25687624f9, 323507be-518f-54a0-ad65-72c91f7296fc, 202962fe-a510-5540-8f09-3222c93f3826, af6ab6d0-258c-5065-88b5-f67717a7550a, b9578b70-b140-513d-8a37-16655a6604b6, 94cd67da-8d84-5b6a-8764-c18500831c82 |
| `0d856b38-89a8-5780-ac25-8c97e712753c` | `0d856b38-89a8-5780-ac25-8c97e712753c` | Người dân địa phương | Hỗ trợ bảo vệ môi trường | 25–50 tuổi | community adult/background_adult | Áo sơ mi ngắn tay, quần âu, giày dép thông thường | a0cb44fd-d264-5076-b0d9-cb525469c082, 202962fe-a510-5540-8f09-3222c93f3826, af6ab6d0-258c-5065-88b5-f67717a7550a, b9578b70-b140-513d-8a37-16655a6604b6, 94cd67da-8d84-5b6a-8764-c18500831c82 |
| `c92a7bf1-39c0-5d6d-83c5-159d77a44d96` | `teacher` | Giáo viên | Giáo viên hướng dẫn hoạt động giáo dục | adult | teacher/supporting | Trang phục nghề nghiệp kín đáo, màu trung tính; không đồng phục học sinh, không khăn quàng đỏ. | 1a443f2c-c582-541f-9d9b-5d25687624f9, 323507be-518f-54a0-ad65-72c91f7296fc |

Teacher was missing from the original scene-3 binding. A deterministic DRAFT CharacterBible was added with ID `c92a7bf1-39c0-5d6d-83c5-159d77a44d96`; it is not approved. Scene 3 now has teacher + student; Scene 4 has teacher supervision + student. Community adult remains distinct and never receives student wardrobe.

## Scene packages v3

### Scene 1 — Mở đầu: Cảnh đồng bằng Bắc Bộ (5s)
- Character mapping: `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` → Tham gia hoạt động bảo vệ môi trường, `0d856b38-89a8-5780-ac25-8c97e712753c` → Hỗ trợ bảo vệ môi trường
- Location: `55284b23-c8ac-5e9e-869f-793081873e00`
- Style: Bright friendly 2D educational animation for Grade 4 learning.
- Subjects: ["recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image", "community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground"]
- Action: Cảnh đồng bằng Bắc Bộ với ruộng lúa xanh mướt, dòng sông chảy qua, bầu trời trong xanh
- Composition: Wide establishing view; subjects small in landscape.
- Camera: WIDE
- Lighting: Soft natural daylight, bright and calm.
- Positive prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery | recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image; community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground | Cảnh đồng bằng Bắc Bộ với ruộng lúa xanh mướt, dòng sông chảy qua, bầu trời trong xanh | Wide establishing view; subjects small in landscape. | WIDE | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water
- Continuity: ["Maintain recurring student identity and outfit across scenes.", "No reference images generated; prompt-only consistency readiness."]
- Workflow metadata: `{"aspect_ratio": "16:9", "base_model_hash": null, "base_model_id": null, "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "55284b23-c8ac-5e9e-869f-793081873e00", "prompt_compiler_version": "structured-visual-prompt-compiler-v3", "reference_status": "NOT_GENERATED", "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Source/resolution IDs: project design source `acc067db-1857-5e82-a040-c32383a6070c`; restricted resolutions retained in grounding records.
- Excluded claims: ["unsupported named plant species", "unsupported architecture"]
- Package: `visual-prompt-package-v3` / `cc801a4b6daafbe789d8586293d83f617d4023c77e6b0a0528e75f71647dbd2a`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 2 — Học sinh đến trường (5s)
- Character mapping: `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` → Tham gia hoạt động bảo vệ môi trường
- Location: `68b8e2a3-517e-5ea2-9c3b-1d40ba9a9002`
- Style: Bright friendly 2D educational animation for Grade 4 learning.
- Subjects: ["recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image"]
- Action: Students arrive with a reusable collection bag and a young tree seedling.
- Composition: Balanced educational composition with clear subject action.
- Camera: MEDIUM_WIDE
- Lighting: Soft natural daylight, bright and calm.
- Positive prompt: Bright friendly 2D educational animation for Grade 4 learning. | simple modern primary school, classroom and schoolyard with trees, no signage text | recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image | Students arrive with a reusable collection bag and a young tree seedling. | Balanced educational composition with clear subject action. | MEDIUM_WIDE | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water
- Continuity: ["Maintain recurring student identity and outfit across scenes.", "No reference images generated; prompt-only consistency readiness."]
- Workflow metadata: `{"aspect_ratio": "16:9", "base_model_hash": null, "base_model_id": null, "character_bible_versions": {"a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182"], "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "68b8e2a3-517e-5ea2-9c3b-1d40ba9a9002", "prompt_compiler_version": "structured-visual-prompt-compiler-v3", "reference_status": "NOT_GENERATED", "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Source/resolution IDs: project design source `acc067db-1857-5e82-a040-c32383a6070c`; restricted resolutions retained in grounding records.
- Excluded claims: ["unsupported named plant species", "unsupported architecture"]
- Package: `visual-prompt-package-v3` / `ee55ffc8c9cdfe64d1ff288079d19ed911419334e715235021a900e4bc33c5af`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 3 — Bài học về bảo vệ môi trường (5s)
- Character mapping: `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` → Tham gia hoạt động bảo vệ môi trường, `c92a7bf1-39c0-5d6d-83c5-159d77a44d96` → Giáo viên hướng dẫn hoạt động giáo dục
- Location: `68b8e2a3-517e-5ea2-9c3b-1d40ba9a9002`
- Style: Bright friendly 2D educational animation for Grade 4 learning.
- Subjects: ["recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image", "teacher: adult, friendly neutral face, modest professional clothing, no student uniform, no red scarf, supportive classroom/outdoor supervisor, no reference image"]
- Action: Teacher explains nature protection while students sit and listen; simple symbol visual aid without text.
- Composition: Balanced educational composition with clear subject action.
- Camera: MEDIUM_WIDE
- Lighting: Soft natural daylight, bright and calm.
- Positive prompt: Bright friendly 2D educational animation for Grade 4 learning. | simple modern primary school, classroom and schoolyard with trees, no signage text | recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image; teacher: adult, friendly neutral face, modest professional clothing, no student uniform, no red scarf, supportive classroom/outdoor supervisor, no reference image | Teacher explains nature protection while students sit and listen; simple symbol visual aid without text. | Balanced educational composition with clear subject action. | MEDIUM_WIDE | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water
- Continuity: ["Maintain recurring student identity and outfit across scenes.", "No reference images generated; prompt-only consistency readiness."]
- Workflow metadata: `{"aspect_ratio": "16:9", "base_model_hash": null, "base_model_id": null, "character_bible_versions": {"a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 1, "c92a7bf1-39c0-5d6d-83c5-159d77a44d96": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "c92a7bf1-39c0-5d6d-83c5-159d77a44d96"], "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "68b8e2a3-517e-5ea2-9c3b-1d40ba9a9002", "prompt_compiler_version": "structured-visual-prompt-compiler-v3", "reference_status": "NOT_GENERATED", "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Source/resolution IDs: project design source `acc067db-1857-5e82-a040-c32383a6070c`; restricted resolutions retained in grounding records.
- Excluded claims: ["unsupported named plant species", "unsupported architecture"]
- Package: `visual-prompt-package-v3` / `e1336724efd773dc191c5825845d3e420fa8f6c5fe71629855c2aaf1e8a3fda4`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 4 — Học sinh ra ngoài thực hành (6s)
- Character mapping: `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` → Tham gia hoạt động bảo vệ môi trường, `c92a7bf1-39c0-5d6d-83c5-159d77a44d96` → Giáo viên hướng dẫn hoạt động giáo dục
- Location: `780190e3-0ab3-596d-979a-42ba8104a1f1`
- Style: Bright friendly 2D educational animation for Grade 4 learning.
- Subjects: ["recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image", "teacher: adult, friendly neutral face, modest professional clothing, no student uniform, no red scarf, supportive classroom/outdoor supervisor, no reference image"]
- Action: Students collect ordinary litter with protective gloves under adult supervision, staying safely away from the water edge.
- Composition: Balanced educational composition with clear subject action.
- Camera: MEDIUM_WIDE
- Lighting: Soft natural daylight, bright and calm.
- Positive prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery | recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image; teacher: adult, friendly neutral face, modest professional clothing, no student uniform, no red scarf, supportive classroom/outdoor supervisor, no reference image | Students collect ordinary litter with protective gloves under adult supervision, staying safely away from the water edge. | Balanced educational composition with clear subject action. | MEDIUM_WIDE | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water
- Continuity: ["Maintain recurring student identity and outfit across scenes.", "No reference images generated; prompt-only consistency readiness."]
- Workflow metadata: `{"aspect_ratio": "16:9", "base_model_hash": null, "base_model_id": null, "character_bible_versions": {"a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 1, "c92a7bf1-39c0-5d6d-83c5-159d77a44d96": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "c92a7bf1-39c0-5d6d-83c5-159d77a44d96"], "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "780190e3-0ab3-596d-979a-42ba8104a1f1", "prompt_compiler_version": "structured-visual-prompt-compiler-v3", "reference_status": "NOT_GENERATED", "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Source/resolution IDs: project design source `acc067db-1857-5e82-a040-c32383a6070c`; restricted resolutions retained in grounding records.
- Excluded claims: ["unsupported named plant species", "unsupported architecture"]
- Package: `visual-prompt-package-v3` / `dc85fbb0738bd0c25cbd73b81778859f453b71613e97cf67b9c0273e311d879b`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 5 — Người dân tham gia (6s)
- Character mapping: `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` → Tham gia hoạt động bảo vệ môi trường, `0d856b38-89a8-5780-ac25-8c97e712753c` → Hỗ trợ bảo vệ môi trường
- Location: `780190e3-0ab3-596d-979a-42ba8104a1f1`
- Style: Bright friendly 2D educational animation for Grade 4 learning.
- Subjects: ["recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image", "community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground"]
- Action: Students and community adults sort ordinary litter and support safe planting.
- Composition: Balanced educational composition with clear subject action.
- Camera: MEDIUM_WIDE
- Lighting: Soft natural daylight, bright and calm.
- Positive prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery | recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image; community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground | Students and community adults sort ordinary litter and support safe planting. | Balanced educational composition with clear subject action. | MEDIUM_WIDE | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water
- Continuity: ["Maintain recurring student identity and outfit across scenes.", "No reference images generated; prompt-only consistency readiness."]
- Workflow metadata: `{"aspect_ratio": "16:9", "base_model_hash": null, "base_model_id": null, "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "780190e3-0ab3-596d-979a-42ba8104a1f1", "prompt_compiler_version": "structured-visual-prompt-compiler-v3", "reference_status": "NOT_GENERATED", "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Source/resolution IDs: project design source `acc067db-1857-5e82-a040-c32383a6070c`; restricted resolutions retained in grounding records.
- Excluded claims: ["unsupported named plant species", "unsupported architecture"]
- Package: `visual-prompt-package-v3` / `7421cb57c0bc8c978811b64c5eacff7e74403d45ae19a90d18103e538f9d3a4e`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 6 — Cây non được trồng (5s)
- Character mapping: `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` → Tham gia hoạt động bảo vệ môi trường, `0d856b38-89a8-5780-ac25-8c97e712753c` → Hỗ trợ bảo vệ môi trường
- Location: `780190e3-0ab3-596d-979a-42ba8104a1f1`
- Style: Bright friendly 2D educational animation for Grade 4 learning.
- Subjects: ["recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image", "community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground"]
- Action: Students and adults plant one young non-specific tree with safe tools under supervision; it remains a young tree.
- Composition: Balanced educational composition with clear subject action.
- Camera: MEDIUM_WIDE
- Lighting: Soft natural daylight, bright and calm.
- Positive prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland riverbank, level horizon, safe distance from water, generic non-specific greenery | recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image; community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground | Students and adults plant one young non-specific tree with safe tools under supervision; it remains a young tree. | Balanced educational composition with clear subject action. | MEDIUM_WIDE | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water
- Continuity: ["Maintain recurring student identity and outfit across scenes.", "No reference images generated; prompt-only consistency readiness."]
- Workflow metadata: `{"aspect_ratio": "16:9", "base_model_hash": null, "base_model_id": null, "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "780190e3-0ab3-596d-979a-42ba8104a1f1", "prompt_compiler_version": "structured-visual-prompt-compiler-v3", "reference_status": "NOT_GENERATED", "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Source/resolution IDs: project design source `acc067db-1857-5e82-a040-c32383a6070c`; restricted resolutions retained in grounding records.
- Excluded claims: ["unsupported named plant species", "unsupported architecture"]
- Package: `visual-prompt-package-v3` / `9ace3911a2863383b19bf42638b65a3788397806e1b83bc03d59f12886e01c9e`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 7 — Thông điệp bảo vệ thiên nhiên (8s)
- Character mapping: `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` → Tham gia hoạt động bảo vệ môi trường, `0d856b38-89a8-5780-ac25-8c97e712753c` → Hỗ trợ bảo vệ môi trường
- Location: `55284b23-c8ac-5e9e-869f-793081873e00`
- Style: Bright friendly 2D educational animation for Grade 4 learning.
- Subjects: ["recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image", "community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground"]
- Action: Wide group composition shows a clean riverbank, flat fields and young planted trees as a positive result.
- Composition: Wide group composition.
- Camera: WIDE
- Lighting: Soft natural daylight, bright and calm.
- Positive prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery | recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image; community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground | Wide group composition shows a clean riverbank, flat fields and young planted trees as a positive result. | Wide group composition. | WIDE | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water
- Continuity: ["Maintain recurring student identity and outfit across scenes.", "No reference images generated; prompt-only consistency readiness."]
- Workflow metadata: `{"aspect_ratio": "16:9", "base_model_hash": null, "base_model_id": null, "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "55284b23-c8ac-5e9e-869f-793081873e00", "prompt_compiler_version": "structured-visual-prompt-compiler-v3", "reference_status": "NOT_GENERATED", "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Source/resolution IDs: project design source `acc067db-1857-5e82-a040-c32383a6070c`; restricted resolutions retained in grounding records.
- Excluded claims: ["unsupported named plant species", "unsupported architecture"]
- Package: `visual-prompt-package-v3` / `0aaa01596a09bc61cd980ce30e833820893a130da32dd1ab74dcf5747dfa7056`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

### Scene 8 — Kết thúc (5s)
- Character mapping: `a0c4fcf8-2fa3-5119-9c60-67f9982ae182` → Tham gia hoạt động bảo vệ môi trường, `0d856b38-89a8-5780-ac25-8c97e712753c` → Hỗ trợ bảo vệ môi trường
- Location: `55284b23-c8ac-5e9e-869f-793081873e00`
- Style: Bright friendly 2D educational animation for Grade 4 learning.
- Subjects: ["recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image", "community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground"]
- Action: Calm panoramic pull-back over the clean peaceful landscape; small distant figures wave.
- Composition: Calm panoramic pull-back.
- Camera: WIDE
- Lighting: Soft natural daylight, bright and calm.
- Positive prompt: Bright friendly 2D educational animation for Grade 4 learning. | flat lowland river-delta landscape, level horizon, broad cultivated fields, generic non-specific greenery | recurring student: age 8–10, friendly neutral face, simple consistent hairstyle, red scarf, short-sleeved white collared shirt, dark navy trousers, simple shoes, clear educational palette, simple footwear, no reference image; community adult: adult age band, friendly neutral face, simple practical everyday clothing, no student uniform, no red scarf, no reference image; background_adult when not foreground | Calm panoramic pull-back over the clean peaceful landscape; small distant figures wave. | Calm panoramic pull-back. | WIDE | Soft natural daylight, bright and calm.
- Negative prompt: high mountains, mountain valley, terraced rice fields, stilt-house village, Chinese/Japanese palace architecture, unrequested modern foreign landmark, fake text, watermark, inconsistent student uniform, unsupported named plant species, dangerous litter, sharp objects, hazardous waste, students standing in water
- Continuity: ["Maintain recurring student identity and outfit across scenes.", "No reference images generated; prompt-only consistency readiness."]
- Workflow metadata: `{"aspect_ratio": "16:9", "base_model_hash": null, "base_model_id": null, "character_bible_versions": {"0d856b38-89a8-5780-ac25-8c97e712753c": 1, "a0c4fcf8-2fa3-5119-9c60-67f9982ae182": 1}, "character_ids": ["a0c4fcf8-2fa3-5119-9c60-67f9982ae182", "0d856b38-89a8-5780-ac25-8c97e712753c"], "consistency_readiness": "PROMPT_ONLY", "environment_bible_version": 1, "environment_id": "55284b23-c8ac-5e9e-869f-793081873e00", "prompt_compiler_version": "structured-visual-prompt-compiler-v3", "reference_status": "NOT_GENERATED", "target_height": 768, "target_width": 1344, "visual_bible_version": 1}`
- Source/resolution IDs: project design source `acc067db-1857-5e82-a040-c32383a6070c`; restricted resolutions retained in grounding records.
- Excluded claims: ["unsupported named plant species", "unsupported architecture"]
- Package: `visual-prompt-package-v3` / `72be785d5ced131c57b9073e553a79138d1ec0daae59aa4cdb54e30f713f5359`
- Governance: DRAFT; release_eligible=false; keyframe_status=NOT_GENERATED

## Versioning and QA gates

- Package counts: v1 SUPERSEDED = 8; v2 SUPERSEDED = 8; v3 ACTIVE = 8. Old rows were preserved.
- Scene 7 and Scene 8 have different action, composition, camera and package hashes.
- Student river activity includes adult supervision, protective gloves and ordinary non-hazardous litter only.
- `flat_delta` is retained only in metadata/grounding records; model-facing prompts use natural-language flat lowland river-delta descriptions.
- Recurring character readiness is `PROMPT_ONLY`; reference status is `NOT_GENERATED`. No `CHARACTER_CONSISTENCY_PASS` is claimed.
- VisualBibleSet remains `IN_REVIEW`; cultural review remains pending.
