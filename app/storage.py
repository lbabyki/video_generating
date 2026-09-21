from pathlib import Path


class LocalStorageProvider:
    """Local-only storage with traversal-safe, relative object keys."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def resolve_key(self, key: str) -> Path:
        candidate = (self.root / key).resolve()
        if self.root not in candidate.parents and candidate != self.root:
            raise ValueError("storage key escapes configured root")
        return candidate

    def put_bytes(self, key: str, content: bytes) -> Path:
        destination = self.resolve_key(key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return destination

    def get_bytes(self, key: str) -> bytes:
        return self.resolve_key(key).read_bytes()
