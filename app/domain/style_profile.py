from dataclasses import dataclass, replace


@dataclass(frozen=True)
class AppliedLoRA:
    lora_id: str
    position: int
    model_strength: float
    clip_strength: float

    def validate(self) -> None:
        if self.position < 0:
            raise ValueError("LoRA position must be non-negative")
        if not 0 <= self.model_strength <= 1.5 or not 0 <= self.clip_strength <= 1.5:
            raise ValueError("model_strength and clip_strength must be between 0 and 1.5")


@dataclass(frozen=True)
class VisualStyleProfileVersion:
    name: str
    version: int
    state: str
    prompt_prefix: str
    negative_prompt: str
    aspect_ratio: str
    loras: tuple[AppliedLoRA, ...]

    def validate(self) -> None:
        if self.version < 1:
            raise ValueError("version must be >= 1")
        positions = [item.position for item in self.loras]
        if positions != sorted(positions) or len(set(positions)) != len(positions):
            raise ValueError("LoRA list must be ordered with unique positions")
        for item in self.loras:
            item.validate()

    def revise(self, **changes: object) -> "VisualStyleProfileVersion":
        if self.state == "APPROVED":
            return replace(self, version=self.version + 1, state="DRAFT", **changes)
        return replace(self, **changes)
