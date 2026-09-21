from dataclasses import dataclass, replace


SCENE_STATES = ("DRAFT", "TECHNICALLY_VALID", "CONTENT_REVIEW_REQUIRED", "CULTURAL_REVIEW_REQUIRED", "APPROVED", "LOCKED")
_NEXT = dict(zip(SCENE_STATES, SCENE_STATES[1:]))


@dataclass(frozen=True)
class CulturalProfile:
    name: str
    version: int
    state: str
    guidance: str

    def revise(self, guidance: str) -> "CulturalProfile":
        if self.state == "APPROVED":
            return CulturalProfile(self.name, self.version + 1, "DRAFT", guidance)
        return replace(self, guidance=guidance)


@dataclass(frozen=True)
class ReferenceSource:
    title: str
    source_url: str
    provenance: str
    license: str

    def validate(self) -> None:
        if not all((self.title, self.source_url, self.provenance, self.license)):
            raise ValueError("reference source requires URL, provenance, and license")


@dataclass(frozen=True)
class DatasetAsset:
    asset_id: str
    source: ReferenceSource
    intended_use: str

    def approve(self) -> str:
        self.source.validate()
        if not self.intended_use:
            raise ValueError("dataset asset requires intended use")
        return "APPROVED"


@dataclass(frozen=True)
class Scene:
    scene_id: str
    state: str = "DRAFT"
    content_review: str = "PENDING"
    cultural_review: str = "PENDING"

    def transition(self) -> "Scene":
        if self.state not in _NEXT:
            raise ValueError(f"scene cannot transition from {self.state}")
        return replace(self, state=_NEXT[self.state])

    def review(self, kind: str, decision: str) -> "Scene":
        if kind not in {"content", "cultural"} or decision not in {"APPROVED", "REJECTED"}:
            raise ValueError("invalid review")
        return replace(self, **{f"{kind}_review": decision})

    def lock(self) -> "Scene":
        if self.state != "APPROVED" or self.content_review != "APPROVED" or self.cultural_review != "APPROVED":
            raise ValueError("content and cultural approval are required before locking")
        return replace(self, state="LOCKED")

    def invalidate(self) -> "Scene":
        return replace(self, state="DRAFT", content_review="PENDING", cultural_review="PENDING")

    def can_release_render(self) -> bool:
        return self.state == "LOCKED" and self.content_review == "APPROVED" and self.cultural_review == "APPROVED"
