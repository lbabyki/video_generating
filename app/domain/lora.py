from dataclasses import dataclass


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
