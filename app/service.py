from datetime import datetime, timezone, timedelta
from typing import Optional

from . import shortener
from .store import InMemoryStore, UrlEntry
from .config import settings


class NotFoundError(Exception):
    pass


class ShortenerService:
    def __init__(self, store: InMemoryStore):
        self.store = store

    def shorten(self, long_url: str, ttl_seconds: Optional[int] = None) -> tuple[str, UrlEntry]:
        ttl = settings.default_ttl_seconds if ttl_seconds is None else ttl_seconds
        if ttl < 0:
            ttl = None
        if ttl is not None:
            ttl = min(ttl, settings.max_ttl_seconds)

        now = datetime.now(timezone.utc)
        expires_at = None if ttl is None or ttl == 0 else now + timedelta(seconds=ttl)

        # attempt with linear probing (nonce)
        for nonce in range(0, 1000):
            code = shortener.generate_short_code(long_url, settings.short_code_length, nonce=nonce)
            entry = self.store.get(code)
            if entry is None:
                url_entry = UrlEntry(original_url=long_url, created_at=now, expires_at=expires_at)
                self.store.save(code, url_entry)
                return code, url_entry
            if entry.original_url == long_url:
                # idempotent: same URL
                return code, entry
            # else collision: continue (linear probing via nonce)

        raise RuntimeError("Unable to generate unique short code after probing")

    def resolve(self, code: str) -> str:
        entry = self.store.get(code)
        if entry is None:
            raise NotFoundError()
        return entry.original_url

    def info(self, code: str) -> UrlEntry:
        entry = self.store.get(code)
        if entry is None:
            raise NotFoundError()
        return entry
