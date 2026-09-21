from dataclasses import dataclass
from pathlib import Path

from app.domain.model import sha256_file


@dataclass(frozen=True)
class LoRAManifest:
    name: str
    base_model: str
    revision: str
    sha256: str
    source_url: str
    license: str
    file_name: str
    default_weight: float = 0.7

    def validate(self) -> None:
        if not self.file_name.endswith(".safetensors"):
            raise ValueError("LoRA weights must use the .safetensors format")
        if len(self.sha256) != 64 or any(char not in "0123456789abcdef" for char in self.sha256.lower()):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        if not all((self.revision, self.source_url, self.license, self.base_model)):
            raise ValueError("base_model, revision, source_url, and license are required")
        if not 0 <= self.default_weight <= 1.5:
            raise ValueError("default_weight must be between 0 and 1.5")


def import_manifest(payload: dict[str, object]) -> LoRAManifest:
    required = ("name", "base_model", "revision", "sha256", "source_url", "license", "file_name")
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"manifest missing required fields: {', '.join(missing)}")
    manifest = LoRAManifest(**{field: payload[field] for field in required}, default_weight=payload.get("default_weight", 0.7))
    manifest.validate()
    return manifest


def transition_state(current: str, target: str) -> str:
    allowed = {"DRAFT": {"APPROVED", "REJECTED"}, "APPROVED": {"RETIRED"}, "REJECTED": set(), "RETIRED": set()}
    if target not in allowed.get(current, set()):
        raise ValueError(f"invalid LoRA state transition: {current} -> {target}")
    return target


@dataclass(frozen=True)
class ControlledLoRA:
    id: str; version: str; lora_type: str; source: str; source_revision: str; filename: str; sha256: str
    compatible_base_model: str; trigger_words: tuple[str, ...]; default_model_strength: float; min_model_strength: float
    max_model_strength: float; default_clip_strength: float; min_clip_strength: float; max_clip_strength: float
    license_id: str; license_review_status: str; review_status: str

    def validate(self, models_dir: Path, model_strength: float | None = None, clip_strength: float | None = None) -> None:
        if self.lora_type not in {"STYLE", "ENVIRONMENT", "CHARACTER"}:
            raise ValueError("MOTION and unsupported LoRA types are forbidden for SDXL image workflows")
        if self.compatible_base_model != "SDXL_BASE" or not self.filename.endswith(".safetensors"):
            raise ValueError("LoRA must be an SDXL_BASE .safetensors file")
        if self.review_status != "APPROVED" or not all((self.source, self.source_revision, self.license_id, self.license_review_status)):
            raise ValueError("LoRA requires approved review status and complete license provenance")
        path = models_dir / self.filename
        if not path.is_file() or sha256_file(path) != self.sha256:
            raise ValueError("LoRA file is missing or SHA-256 mismatches manifest")
        for value, low, high in ((model_strength if model_strength is not None else self.default_model_strength, self.min_model_strength, self.max_model_strength), (clip_strength if clip_strength is not None else self.default_clip_strength, self.min_clip_strength, self.max_clip_strength)):
            if not low <= value <= high:
                raise ValueError("LoRA strength is outside approved range")
