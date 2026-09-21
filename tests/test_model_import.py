import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.domain.model import ModelManifest, sha256_file, validate_download, validate_safetensors
from app.model_import import _safe_target, import_checkpoint


ROOT = Path(__file__).parents[1]


def manifest_payload() -> dict[str, object]:
    return json.loads((ROOT / "manifests/sdxl-base-1.0.json").read_text())


def write_safetensors(path: Path) -> None:
    header = b'{"tensor":{"dtype":"F32","shape":[1],"data_offsets":[0,4]}}'
    path.write_bytes(len(header).to_bytes(8, "little") + header + b"\x00\x00\x00\x00")


class ModelImportTests(unittest.TestCase):
    def test_manifest_requires_safetensors_pinned_revision_and_license(self) -> None:
        payload = manifest_payload()
        ModelManifest.from_dict(payload)
        payload["source_filename"] = "unsafe.ckpt"
        with self.assertRaises(ValueError):
            ModelManifest.from_dict(payload)
        payload = manifest_payload()
        payload["source_revision"] = "main"
        with self.assertRaises(ValueError):
            ModelManifest.from_dict(payload)
        payload = manifest_payload()
        payload["license_url"] = ""
        with self.assertRaises(ValueError):
            ModelManifest.from_dict(payload)

    def test_sha_mismatch_and_invalid_safetensors_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            file_path = Path(temporary) / "model.safetensors"
            write_safetensors(file_path)
            validate_safetensors(file_path)
            payload = manifest_payload()
            payload.update({"local_filename": file_path.name, "source_filename": file_path.name, "file_size": file_path.stat().st_size, "sha256": "0" * 64})
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                validate_download(file_path, ModelManifest.from_dict(payload))
            bad = Path(temporary) / "bad.safetensors"
            bad.write_bytes(b"not-safe")
            with self.assertRaises(ValueError):
                validate_safetensors(bad)

    def test_staging_and_output_paths_cannot_traverse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                _safe_target(root, "../escape.safetensors")
            partial = root / "partial.safetensors.part"
            partial.write_bytes(b"partial")
            self.assertFalse((root / "model.safetensors").exists())
            self.assertEqual(partial.read_bytes(), b"partial")

    def test_bad_content_range_restarts_instead_of_appending_partial(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = ModelManifest.from_dict(manifest_payload())
            partial = root / ".staging" / f"{manifest.local_filename}.part"
            partial.parent.mkdir()
            partial.write_bytes(b"stale")
            response = MagicMock()
            response.status = 206
            response.headers.get.return_value = "bytes 0-3/4"
            response.read.side_effect = [b"fresh", b""]
            response.__enter__.return_value = response
            with patch("app.model_import.urlopen", return_value=response), patch("app.model_import.validate_download", side_effect=ValueError("expected test stop")):
                with self.assertRaisesRegex(ValueError, "expected test stop"):
                    import_checkpoint(manifest, root)
            self.assertEqual(partial.read_bytes(), b"fresh")

    def test_model_and_output_runtime_paths_are_gitignored(self) -> None:
        for path in ("models/checkpoints/example.safetensors", "models/checkpoints/.staging/example.part", "output/phase1b/example.png"):
            result = subprocess.run(["git", "check-ignore", path], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_manifest_hash_helper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            file_path = Path(temporary) / "a.bin"
            file_path.write_bytes(b"abc")
            self.assertEqual(sha256_file(file_path), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
