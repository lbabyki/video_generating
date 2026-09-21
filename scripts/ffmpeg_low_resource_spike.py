#!/usr/bin/env python3
"""CPU-only FFmpeg/FFprobe smoke test. It does not use GPU, models, or assets."""

import json
import subprocess
import tempfile
from pathlib import Path


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=True)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="evs-ffmpeg-") as raw_dir:
        output = Path(raw_dir) / "low-resource-smoke.mp4"
        run("ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=navy:s=640x360:r=12:d=1",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", str(output))
        probe = run("ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name,width,height",
                    "-of", "json", str(output))
        metadata = json.loads(probe.stdout)
        stream = metadata["streams"][0]
        assert stream["codec_name"] == "h264"
        assert (stream["width"], stream["height"]) == (640, 360)
        assert float(metadata["format"]["duration"]) > 0
        print(json.dumps({"status": "PASS", "codec": "h264", "resolution": "640x360", "gpu_used": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
