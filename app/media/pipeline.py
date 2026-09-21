import json
import subprocess
from pathlib import Path

from app.media.low_resource import image_sequence_to_mp4_command


def validate_mp4(path: Path) -> dict[str, object]:
    if path.suffix != ".mp4" or not path.is_file() or path.stat().st_size == 0:
        raise ValueError("expected a non-empty .mp4 output")
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name",
                             "-of", "json", str(path)], text=True, capture_output=True, check=True)
    metadata = json.loads(result.stdout)
    if not metadata.get("streams") or float(metadata["format"]["duration"]) <= 0:
        raise ValueError("ffprobe could not validate video output")
    return metadata


def render_low_resource_job(frames_glob: str, output: Path, fps: int = 12) -> dict[str, object]:
    if ".." in Path(frames_glob).parts:
        raise ValueError("frame glob must not traverse parent directories")
    output = output.resolve()
    if output.exists():
        return {"status": "idempotent", "output": str(output), "metadata": validate_mp4(output)}
    partial = output.with_suffix(output.suffix + ".partial")
    if partial.exists():
        raise RuntimeError("partial output exists; clean it before retrying")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = image_sequence_to_mp4_command(frames_glob, partial, fps)
    try:
        subprocess.run(command, text=True, capture_output=True, check=True)
        partial.replace(output)
        return {"status": "created", "output": str(output), "metadata": validate_mp4(output)}
    except Exception:
        partial.unlink(missing_ok=True)
        raise
