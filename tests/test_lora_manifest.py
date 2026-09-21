import unittest

from app.domain.lora import LoRAManifest, import_manifest, transition_state


class LoRAManifestTests(unittest.TestCase):
    def test_accepts_complete_safetensors_manifest(self) -> None:
        manifest = LoRAManifest("lesson-style", "sdxl-base-1.0", "abc123", "a" * 64,
                                "https://example.invalid/model", "LicenseRef-Approved", "style.safetensors")
        manifest.validate()

    def test_rejects_non_safetensors_weight(self) -> None:
        manifest = LoRAManifest("bad", "sdxl", "rev", "a" * 64,
                                "https://example.invalid/model", "license", "bad.ckpt")
        with self.assertRaises(ValueError):
            manifest.validate()

    def test_import_requires_provenance_and_valid_transition(self) -> None:
        with self.assertRaises(ValueError):
            import_manifest({"name": "missing"})
        self.assertEqual(transition_state("DRAFT", "APPROVED"), "APPROVED")
        with self.assertRaises(ValueError):
            transition_state("APPROVED", "DRAFT")
