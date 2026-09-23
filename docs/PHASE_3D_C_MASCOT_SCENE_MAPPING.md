# Phase 3D-C — BI Mascot Review, Scene Mapping and Visual Prompt v5

Status: `MASCOT_SCENE_MAPPING_READY_FOR_CULTURAL_REVIEW`

- VisualBibleSet v1: `9f2272dd-2237-53ed-a3aa-fd570e89a75e` APPROVED and unchanged.
- VisualBibleSet v2: `6d9297b4-b762-5b2c-90b1-54fd144592b5` remains DRAFT.
- Mascot CharacterBible remains APPROVED_WITH_RESTRICTIONS; training permission remains PENDING.
- No inference, rendering, training, v5 media generation or LoRA export was run.

## Overlay policy

- Dedicated overlay layer; alpha required; max mascot height 22%; outer margin 4%; subtitle-safe bottom 18%.
- No mirroring, stretching or automatic physical insertion into SDXL scene prompts.
- BI does not replace human roles and must not cover subtitles, faces, hands, safety actions or cultural evidence.

### Scene binding 1
- Scene: `1a443f2c-c582-541f-9d9b-5d25687624f9`
- Asset: `STUDYING_SIDE.png` (`5bf33163-884a-584b-9070-6e7a4f09f927`)
- Expression/role: `STUDYING_SIDE` / `learning inset`
- Anchor: `right`; entrance `inset fade`; exit `none`; motion `subtle vertical bounce`
- Prop-bearing/inset-only: `True` / `True`
- Package: `visual-prompt-package-v5` / `04b29a30627955d3b5a07807df113d59774c089320d3f7676f647f7c76dad3ab`
- Model-facing prompts unchanged from v4 and contain no mascot ID, filename or overlay token.

### Scene binding 2
- Scene: `202962fe-a510-5540-8f09-3222c93f3826`
- Asset: `DETERMINED.png` (`3b7f57fb-e219-57f2-97ee-e035090cc002`)
- Expression/role: `DETERMINED` / `call to action`
- Anchor: `right`; entrance `gentle entrance`; exit `none`; motion `subtle scale`
- Prop-bearing/inset-only: `False` / `False`
- Package: `visual-prompt-package-v5` / `39997a40959dce3003a77ae57401e335c3326499fab8cb65742ef9ee4dc58398`
- Model-facing prompts unchanged from v4 and contain no mascot ID, filename or overlay token.

### Scene binding 3
- Scene: `323507be-518f-54a0-ad65-72c91f7296fc`
- Asset: `WORRIED.png` (`d6af7c84-cbbd-5d40-8d95-802d8773fbc4`)
- Expression/role: `WORRIED` / `environmental concern`
- Anchor: `left`; entrance `gentle entrance`; exit `none`; motion `subtle entrance`
- Prop-bearing/inset-only: `False` / `False`
- Package: `visual-prompt-package-v5` / `b6ab30d7ec8780dea5da54b7a1b83b8dd8011d9f66c603cb9d7671b8c35db81c`
- Model-facing prompts unchanged from v4 and contain no mascot ID, filename or overlay token.

### Scene binding 4
- Scene: `94cd67da-8d84-5b6a-8764-c18500831c82`
- Asset: `GREETING.png` (`d63f1dec-1c7e-53aa-a5cd-e52b4522a26a`)
- Expression/role: `GREETING` / `closing`
- Anchor: `left`; entrance `gentle entrance`; exit `soft fade`; motion `subtle fade`
- Prop-bearing/inset-only: `False` / `False`
- Package: `visual-prompt-package-v5` / `bd377ca2b563865340f64aec463fd1e1f2e397b50d2796dad7965e2a07fdc108`
- Model-facing prompts unchanged from v4 and contain no mascot ID, filename or overlay token.

### Scene binding 5
- Scene: `a0cb44fd-d264-5076-b0d9-cb525469c082`
- Asset: `GREETING.png` (`d63f1dec-1c7e-53aa-a5cd-e52b4522a26a`)
- Expression/role: `GREETING` / `introduction`
- Anchor: `right`; entrance `gentle entrance`; exit `none`; motion `subtle entrance`
- Prop-bearing/inset-only: `False` / `False`
- Package: `visual-prompt-package-v5` / `2a83d0d9c08e41f21c138115ecc8d9fe937eea7619aa8aeb7151088a72eb00fa`
- Model-facing prompts unchanged from v4 and contain no mascot ID, filename or overlay token.

### Scene binding 6
- Scene: `af6ab6d0-258c-5065-88b5-f67717a7550a`
- Asset: `FRIENDLY_SMILE.png` (`94ea16e5-b533-5e3c-b173-d0ff7447d28d`)
- Expression/role: `FRIENDLY_SMILE` / `positive reinforcement`
- Anchor: `left`; entrance `gentle entrance`; exit `none`; motion `subtle scale`
- Prop-bearing/inset-only: `False` / `False`
- Package: `visual-prompt-package-v5` / `8afe03d9cfd0dabb2d6c8462f498701071cc3059b6f84c21375aec6997e3f88a`
- Model-facing prompts unchanged from v4 and contain no mascot ID, filename or overlay token.

### Scene binding 7
- Scene: `b9578b70-b140-513d-8a37-16655a6604b6`
- Asset: `DETERMINED.png` (`3b7f57fb-e219-57f2-97ee-e035090cc002`)
- Expression/role: `DETERMINED` / `message emphasis`
- Anchor: `right`; entrance `gentle entrance`; exit `none`; motion `subtle vertical bounce`
- Prop-bearing/inset-only: `False` / `False`
- Package: `visual-prompt-package-v5` / `f21ca09c57351f5e48fe725883bc922c1644916f7811278b12fd4f55cfb09a99`
- Model-facing prompts unchanged from v4 and contain no mascot ID, filename or overlay token.

### Scene binding 8
- Scene: `cc77b771-374c-52d9-bf62-53b1f4d58064`
- Asset: `FRIENDLY_SMILE.png` (`94ea16e5-b533-5e3c-b173-d0ff7447d28d`)
- Expression/role: `FRIENDLY_SMILE` / `encouragement`
- Anchor: `left`; entrance `gentle fade`; exit `none`; motion `subtle scale`
- Prop-bearing/inset-only: `False` / `False`
- Package: `visual-prompt-package-v5` / `95ec2c6654da7bb444f29da5a4f8952d999e216a05514f607f5a6d3f3b002275`
- Model-facing prompts unchanged from v4 and contain no mascot ID, filename or overlay token.

## Cultural governance

- New v2 requirement: `4b4a212e-c942-5574-a6a7-47911adc3741`, status `PENDING`: BI remains a non-human overlay guide and does not replace human student, teacher or community roles.
- Cultural approval from v1 was not transferred automatically.
- v1–v4 records and hashes remain unchanged; v4 was not superseded.
- `STUDYING_SIDE` is runtime reference only, prop-bearing, and excluded from identity-only training.
- Scene 1 and Scene 8 both use GREETING but differ in anchor and motion/exit metadata.

## Package state

- Exactly 8 v5 packages and 8 mascot scene bindings exist.
- v5 packages are ACTIVE, DRAFT, `release_eligible=false`, `keyframe_status=NOT_GENERATED`, `lora_status=NOT_ASSIGNED`.
- No claim of `VISUAL_BIBLE_V2_APPROVED`, `CULTURAL_REVIEW_V2_APPROVED`, `OVERLAY_RENDER_PASS`, `TRAINING_READY`, `LORA_PASS`, `KEYFRAME_PASS` or `PROMPT_TO_VIDEO_PASS`.

## Verification

- All 8 bindings reference assets reviewed `APPROVED_FOR_REFERENCE`.
- No mascot UUID, filename or internal token appears in model-facing prompts.
- Scene 4 safety constraints remain in copied v4 prompts.
- Source mascot PNGs remain outside the repository and untracked.
