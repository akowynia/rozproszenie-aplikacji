from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class UrlEntry:
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime]


class InMemoryStore:
    def __init__(self):
        self._data: dict[str, UrlEntry] = {}

    def save(self, code: str, entry: UrlEntry) -> None:
        self._data[code] = entry

    def get(self, code: str) -> Optional[UrlEntry]:
        entry = self._data.get(code)
        if entry is None:
            return None
        if entry.expires_at and datetime.now(timezone.utc) > entry.expires_at:
            del self._data[code]
            return None
        return entry

    def exists(self, code: str) -> bool:
        return self.get(code) is not None

    def delete_expired(self) -> int:
        now = datetime.now(timezone.utc)
        expired = [k for k, v in self._data.items() if v.expires_at and now > v.expires_at]
        for k in expired:
            del self._data[k]
        return len(expired)
