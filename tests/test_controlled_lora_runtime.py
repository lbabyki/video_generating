import hashlib
import tempfile
import unittest
from pathlib import Path
from app.domain.lora import ControlledLoRA
from app.workflows import build_sdxl_baseline, build_sdxl_lora_variant, lora_snapshot

def make_lora(**x):
    d=dict(id="style",version="1",lora_type="STYLE",source="https://official.example",source_revision="a"*40,filename="style.safetensors",sha256="",compatible_base_model="SDXL_BASE",trigger_words=("style",),default_model_strength=.7,min_model_strength=.4,max_model_strength=1.,default_clip_strength=.7,min_clip_strength=.4,max_clip_strength=1.,license_id="openrail",license_review_status="REVIEWED",review_status="APPROVED"); d.update(x); return ControlledLoRA(**d)

class ControlledLoRATests(unittest.TestCase):
    def test_variant_b_and_ordered_c(self):
        self.assertNotIn("LoraLoader", {x["class_type"] for x in build_sdxl_baseline("x.safetensors").values()})
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/"style.safetensors").write_bytes(b"a"); (root/"env.safetensors").write_bytes(b"b")
            a=make_lora(sha256=hashlib.sha256(b"a").hexdigest()); b=make_lora(id="env",lora_type="ENVIRONMENT",filename="env.safetensors",sha256=hashlib.sha256(b"b").hexdigest())
            a.validate(root,.7,.7); b.validate(root,.8,.8); w=build_sdxl_lora_variant("x.safetensors",[(a,.7,.7),(b,.8,.8)])
            self.assertEqual(w["11"]["inputs"]["model"],["10",0]); self.assertEqual(len(lora_snapshot({"id":"m","sha256":"x"},[(a,.7,.7),(b,.8,.8)],"p",1,w)["loras"]),2)

    def test_rejections(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/"style.safetensors").write_bytes(b"a"); h=hashlib.sha256(b"a").hexdigest()
            for bad in (make_lora(compatible_base_model="SD15",sha256=h),make_lora(sha256="0"*64),make_lora(review_status="BLOCKED",sha256=h),make_lora(review_status="DEPRECATED",sha256=h),make_lora(review_status="DRAFT",sha256=h),make_lora(lora_type="MOTION",sha256=h)):
                with self.assertRaises(ValueError): bad.validate(root,.7,.7)
            with self.assertRaises(ValueError): make_lora(sha256=h).validate(root,1.2,.7)
