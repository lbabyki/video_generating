import tempfile
import unittest
from pathlib import Path

from app.storage import LocalStorageProvider


class LocalStorageProviderTests(unittest.TestCase):
    def test_round_trip_and_rejects_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = LocalStorageProvider(Path(temporary))
            store.put_bytes("projects/demo.txt", b"safe")
            self.assertEqual(store.get_bytes("projects/demo.txt"), b"safe")
            with self.assertRaises(ValueError):
                store.resolve_key("../outside.txt")
