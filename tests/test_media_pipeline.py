import subprocess
import tempfile
import unittest
from pathlib import Path

from app.media.pipeline import render_low_resource_job, validate_mp4


class MediaPipelineTests(unittest.TestCase):
    def test_validation_and_idempotency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "clip.mp4"
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=s=64x64:d=0.2", "-c:v", "libx264", str(output)],
                           check=True, capture_output=True, text=True)
            self.assertTrue(validate_mp4(output)["streams"])
            result = render_low_resource_job("frames/*.png", output)
            self.assertEqual(result["status"], "idempotent")

    def test_rejects_traversal_and_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "clip.mp4"
            with self.assertRaises(ValueError):
                render_low_resource_job("../frames/*.png", output)
            output.with_suffix(".mp4.partial").write_bytes(b"partial")
            with self.assertRaises(RuntimeError):
                render_low_resource_job("frames/*.png", output)
