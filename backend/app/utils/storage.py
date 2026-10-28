"""Local file storage."""
import uuid
from pathlib import Path

from ..config.settings import get_settings
from .constants import MAX_UPLOAD_BYTES
from .exceptions import NotFound, ValidationFailed
from .validators import sanitize_filename


class LocalStorage:
    def __init__(self, root: str | None = None):
        self.root = Path(root or get_settings().storage_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if self.root not in path.parents:
            raise ValidationFailed("Invalid storage key")
        return path

    def save(self, filename: str, content: bytes) -> str:
        if len(content) > MAX_UPLOAD_BYTES:
            raise ValidationFailed("File too large")
        key = f"{uuid.uuid4().hex}_{sanitize_filename(filename)}"
        self._path(key).write_bytes(content)
        return key

    def read(self, key: str) -> bytes:
        path = self._path(key)
        if not path.is_file():
            raise NotFound("File not found")
        return path.read_bytes()

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)
