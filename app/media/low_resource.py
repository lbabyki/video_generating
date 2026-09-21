from pathlib import Path


def image_sequence_to_mp4_command(frames_glob: str, output: Path, fps: int = 12) -> list[str]:
    """Build a low-resource, CPU-only H.264 encode command."""
    if fps < 1 or fps > 30:
        raise ValueError("fps must be between 1 and 30 for LOW_RESOURCE mode")
    return [
        "ffmpeg", "-y", "-framerate", str(fps), "-pattern_type", "glob", "-i", frames_glob,
        "-vf", "scale='min(1280,iw)':-2:flags=lanczos,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-movflags", "+faststart",
        str(output),
    ]
