# Phase 3D-D — Cultural Approval v2 and Atomic Package Promotion

Status: `VISUAL_BIBLE_V2_APPROVED_V5_ACTIVE`

- Cultural reviewer: `241e7b2d-9d76-4caa-97d8-9796478a5fa0` (`CULTURAL_REVIEWER`, `ACTIVE`).
- Requirement `4b4a212e-c942-5574-a6a7-47911adc3741`: `APPROVED_WITH_RESTRICTED_SCOPE`.
- VisualBibleSet v1: `APPROVED` and unchanged.
- VisualBibleSet v2: `APPROVED`.
- No inference, rendering, training or media generation ran.

## Package promotion

| Version | Before | After | Runtime selectable |
|---|---|---|---|
| v4 | ACTIVE | SUPERSEDED | false |
| v5 | CANDIDATE | ACTIVE | true |

- Promotion occurred atomically after all eight scene gates passed.
- v5 remains `DRAFT`, `release_eligible=false`, `keyframe_status=NOT_GENERATED`, `lora_status=NOT_ASSIGNED`.
- All v4/v5 prompt content and hashes remain unchanged.

## Resolver results

| Order | Title | Scene ID | Resolver result | v5 package/hash |
| 1 | Mở đầu: Cảnh đồng bằng Bắc Bộ | `a0cb44fd-d264-5076-b0d9-cb525469c082` | v5 | `4c8b44c1-b2e4-5f53-838c-bf844cfcbfad` / `2a83d0d9c08e41f21c138115ecc8d9fe937eea7619aa8aeb7151088a72eb00fa` |
| 2 | Học sinh đến trường | `cc77b771-374c-52d9-bf62-53b1f4d58064` | v5 | `034bac14-d402-5120-b0b6-06a0c0fd0f31` / `95ec2c6654da7bb444f29da5a4f8952d999e216a05514f607f5a6d3f3b002275` |
| 3 | Bài học về bảo vệ môi trường | `1a443f2c-c582-541f-9d9b-5d25687624f9` | v5 | `613fb4fc-19e7-5063-b77a-4571e629933d` / `04b29a30627955d3b5a07807df113d59774c089320d3f7676f647f7c76dad3ab` |
| 4 | Học sinh ra ngoài thực hành | `323507be-518f-54a0-ad65-72c91f7296fc` | v5 | `27c90838-2d25-5d3e-8c97-5f47250a8911` / `b6ab30d7ec8780dea5da54b7a1b83b8dd8011d9f66c603cb9d7671b8c35db81c` |
| 5 | Người dân tham gia | `202962fe-a510-5540-8f09-3222c93f3826` | v5 | `86f06929-3c17-5038-8f79-d68fea54871a` / `39997a40959dce3003a77ae57401e335c3326499fab8cb65742ef9ee4dc58398` |
| 6 | Cây non được trồng | `af6ab6d0-258c-5065-88b5-f67717a7550a` | v5 | `7af10cd2-0b7b-5285-b09d-bf955c2c544d` / `8afe03d9cfd0dabb2d6c8462f498701071cc3059b6f84c21375aec6997e3f88a` |
| 7 | Thông điệp bảo vệ thiên nhiên | `b9578b70-b140-513d-8a37-16655a6604b6` | v5 | `f5e00745-f9f4-5d90-b9fc-4dd5ee26d4ca` / `f21ca09c57351f5e48fe725883bc922c1644916f7811278b12fd4f55cfb09a99` |
| 8 | Kết thúc | `94cd67da-8d84-5b6a-8764-c18500831c82` | v5 | `dcae9280-2e5b-54d0-9235-f248fa826cce` / `bd377ca2b563865340f64aec463fd1e1f2e397b50d2796dad7965e2a07fdc108` |

## Governance

- Mascot assets remain `APPROVED_FOR_REFERENCE`; all training permissions remain `PENDING`.
- Mascot CharacterBible remains `APPROVED_WITH_RESTRICTIONS`.
- No LoRA training permission, dataset approval, overlay render pass, keyframe pass or production render lock was granted.
- Scene 4 safety constraints remain present and v1 human cultural restrictions remain inherited.

## Verification

- Reviewer role/status and all preflight gates passed.
- Exactly one runtime-selectable v5 package exists for each of 8 scenes; v4 is never returned.
- No mascot token appears in model-facing prompts.
- Cultural review, approval and promotion audit events were stored.
