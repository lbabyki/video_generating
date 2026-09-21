import subprocess
import sys
import unittest
from pathlib import Path


class FFmpegSpikeTests(unittest.TestCase):
    def test_cpu_only_spike(self) -> None:
        script = Path(__file__).parents[1] / "scripts" / "ffmpeg_low_resource_spike.py"
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, check=True)
        self.assertIn('"status": "PASS"', result.stdout)
