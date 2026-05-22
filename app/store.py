import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from cassandra.cluster import Session

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

class CassandraStore:
    def __init__(self, session: Session):
        self.session = session

    async def save(self, code: str, entry: UrlEntry) -> None:
        query = (
            "INSERT INTO urls (code, original_url, created_at, expires_at) "
            "VALUES (%s, %s, %s, %s)"
        )
        
        ttl = None
        if entry.expires_at:
            delta = entry.expires_at - datetime.now(timezone.utc)
            ttl = max(1, int(delta.total_seconds()))

        if ttl is not None:
            query_ttl = f"{query} USING TTL %s"
            await asyncio.to_thread(
                self.session.execute,
                query_ttl,
                (code, entry.original_url, entry.created_at, entry.expires_at, ttl)
            )
        else:
            await asyncio.to_thread(
                self.session.execute,
                query,
                (code, entry.original_url, entry.created_at, entry.expires_at)
            )

    async def get(self, code: str) -> Optional[UrlEntry]:
        query = "SELECT original_url, created_at, expires_at FROM urls WHERE code = %s"
        result = await asyncio.to_thread(self.session.execute, query, (code,))
        row = result.one()
        if row is None:
            return None

        expires_at = row.expires_at
        if expires_at:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires_at:
                await self.delete(code)
                return None

        return UrlEntry(
            original_url=row.original_url,
            created_at=row.created_at,
            expires_at=row.expires_at
        )

    async def delete(self, code: str) -> bool:
        exists_query = "SELECT code FROM urls WHERE code = %s"
        result = await asyncio.to_thread(self.session.execute, exists_query, (code,))
        if not result.one():
            return False

        delete_query = "DELETE FROM urls WHERE code = %s"
        await asyncio.to_thread(self.session.execute, delete_query, (code,))
        return True
