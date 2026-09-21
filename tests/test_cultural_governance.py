import unittest

from app.governance.service import CulturalProfile, DatasetAsset, ReferenceSource, Scene


class CulturalGovernanceTests(unittest.TestCase):
    def test_scene_state_machine_and_release_gate(self) -> None:
        scene = Scene("scene-1")
        self.assertFalse(scene.can_release_render())
        for _ in range(4):
            scene = scene.transition()
        self.assertEqual(scene.state, "APPROVED")
        with self.assertRaises(ValueError):
            scene.lock()
        scene = scene.review("content", "APPROVED").review("cultural", "APPROVED").lock()
        self.assertEqual(scene.state, "LOCKED")
        self.assertTrue(scene.can_release_render())

    def test_prompt_or_reference_change_invalidates_approval(self) -> None:
        scene = Scene("scene-2", "APPROVED", "APPROVED", "APPROVED")
        invalidated = scene.invalidate()
        self.assertEqual((invalidated.state, invalidated.content_review, invalidated.cultural_review), ("DRAFT", "PENDING", "PENDING"))

    def test_approved_profile_is_revised_not_mutated(self) -> None:
        approved = CulturalProfile("northern-delta", 1, "APPROVED", "v1")
        revision = approved.revise("v2")
        self.assertEqual((approved.version, approved.guidance), (1, "v1"))
        self.assertEqual((revision.version, revision.state, revision.guidance), (2, "DRAFT", "v2"))

    def test_dataset_asset_without_license_is_rejected(self) -> None:
        source = ReferenceSource("unknown", "https://example.invalid/source", "archive", "")
        with self.assertRaises(ValueError):
            DatasetAsset("asset-1", source, "training").approve()

    def test_reference_requires_provenance(self) -> None:
        with self.assertRaises(ValueError):
            ReferenceSource("source", "https://example.invalid", "", "CC-BY-4.0").validate()
