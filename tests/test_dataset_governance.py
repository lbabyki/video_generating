import hashlib, tempfile, unittest
from pathlib import Path
from app.dataset_governance import DatasetAsset, DatasetVersion, near_duplicate, split_assets, training_export, validate_image, validate_path
def asset(**x):
 d=dict(id="a",dataset_id="d",filename="a.png",sha256="a"*64,perceptual_hash="0"*16,dimensions=(512,512),source_url="https://source",source_type="licensed",creator="artist",license_id="CC",license_url="https://license",ml_training_permission="YES",commercial_use_status="ALLOWED",consent_status="N/A",caption_vi="Ảnh",caption_en="Image",cultural_labels=(),review_status="QUARANTINED",reviewer_audit="",source_group="scene1"); d.update(x); return DatasetAsset(**d)
class DatasetTests(unittest.TestCase):
 def test_validation_traversal_corruption_and_type(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t); p=r/"a.png"; p.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"+(512).to_bytes(4,"big")+(512).to_bytes(4,"big"))
   self.assertEqual(validate_image(p),(512,512))
   with self.assertRaises(ValueError): validate_path(r,"../x.png")
   bad=r/"bad.jpg"; bad.write_bytes(b"bad")
   with self.assertRaises(ValueError): validate_image(bad)
 def test_license_review_duplicates_split_and_immutable(self):
  x=asset().transition("VALIDATED").transition("CULTURAL_REVIEWED").transition("APPROVED","r")
  self.assertEqual(training_export([x,asset(commercial_use_status="UNKNOWN")]),[x]); self.assertTrue(near_duplicate("0"*16,"0"*15+"1"))
  with self.assertRaises(ValueError): asset().transition("APPROVED","r")
  self.assertEqual(DatasetVersion("d",1,"STYLE","t").freeze().revise().version,2)
  a,b=split_assets([x,asset(id="b",source_group="scene1"),asset(id="c",source_group="scene2")]); self.assertEqual({z.source_group for z in a}&{z.source_group for z in b},set())
