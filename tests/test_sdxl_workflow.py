import unittest

from app.domain.model import ModelManifest
from app.workflows import BASELINE_SEED, build_sdxl_baseline, validate_baseline_workflow, workflow_sha256


class SDXLBaselineWorkflowTests(unittest.TestCase):
    def test_workflow_is_reproducible_and_has_no_lora_or_custom_nodes(self) -> None:
        first = build_sdxl_baseline("sd_xl_base_1.0.safetensors")
        second = build_sdxl_baseline("sd_xl_base_1.0.safetensors")
        self.assertEqual(workflow_sha256(first), workflow_sha256(second))
        sampler = first["5"]["inputs"]
        self.assertEqual((sampler["seed"], sampler["steps"], sampler["cfg"]), (BASELINE_SEED, 25, 6.5))
        self.assertNotIn("LoraLoader", {node["class_type"] for node in first.values()})

    def test_workflow_rejects_lora_node(self) -> None:
        workflow = build_sdxl_baseline("sd_xl_base_1.0.safetensors")
        workflow["8"] = {"class_type": "LoraLoader", "inputs": {}}
        with self.assertRaises(ValueError):
            validate_baseline_workflow(workflow)

    def test_cultural_variant_only_changes_prompts_and_output_prefix(self) -> None:
        baseline = build_sdxl_baseline("sd_xl_base_1.0.safetensors")
        variant = build_sdxl_baseline("sd_xl_base_1.0.safetensors", positive_prompt="cultural prompt", negative_prompt="cultural negative", filename_prefix="phase1c/experiment-001/variant-b-base-no-lora")
        self.assertEqual(baseline["4"]["inputs"], variant["4"]["inputs"])
        self.assertEqual(baseline["5"]["inputs"], variant["5"]["inputs"])
        self.assertEqual(variant["2"]["inputs"]["text"], "cultural prompt")
        self.assertEqual(variant["3"]["inputs"]["text"], "cultural negative")

    def test_unapproved_model_cannot_be_used(self) -> None:
        payload = {
            "id": "test", "name": "test", "model_type": "CHECKPOINT", "architecture": "SDXL_BASE",
            "source_repository": "owner/repo", "source_revision": "a" * 40,
            "source_filename": "a.safetensors", "local_filename": "a.safetensors", "sha256": "b" * 64,
            "file_size": 1, "format": "SAFETENSORS", "compatible_workflow": "phase1b-sdxl-base-v1",
            "license_id": "license", "license_url": "https://example.invalid/license",
            "license_review_status": "PENDING", "commercial_use": "UNKNOWN", "review_status": "DRAFT",
        }
        self.assertFalse(ModelManifest.from_dict(payload).is_approved())
