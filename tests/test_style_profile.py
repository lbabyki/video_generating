import unittest

from app.domain.style_profile import AppliedLoRA, VisualStyleProfileVersion


class VisualStyleProfileTests(unittest.TestCase):
    def test_approved_profile_creates_new_draft_version(self) -> None:
        profile = VisualStyleProfileVersion("science", 1, "APPROVED", "flat educational", "", "16:9",
                                            (AppliedLoRA("lora-1", 0, 0.7, 0.5),))
        profile.validate()
        revision = profile.revise(prompt_prefix="revised")
        self.assertEqual((revision.version, revision.state, revision.prompt_prefix), (2, "DRAFT", "revised"))

    def test_rejects_invalid_strength_or_order(self) -> None:
        profile = VisualStyleProfileVersion("science", 1, "DRAFT", "x", "", "16:9",
                                            (AppliedLoRA("a", 1, 0.7, 0.5), AppliedLoRA("b", 0, 0.7, 0.5)))
        with self.assertRaises(ValueError):
            profile.validate()
