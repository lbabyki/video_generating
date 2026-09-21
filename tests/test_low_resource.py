import unittest
from pathlib import Path

from app.media.low_resource import image_sequence_to_mp4_command


class LowResourceCommandTests(unittest.TestCase):
    def test_cpu_command_is_bounded(self) -> None:
        command = image_sequence_to_mp4_command("frames/*.png", Path("out.mp4"))
        self.assertIn("libx264", command)
        self.assertNotIn("h264_nvenc", command)
        self.assertIn("veryfast", command)

    def test_rejects_high_fps(self) -> None:
        with self.assertRaises(ValueError):
            image_sequence_to_mp4_command("frames/*.png", Path("out.mp4"), fps=31)
