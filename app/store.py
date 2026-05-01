from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .database import UrlModel

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

class SqlAlchemyStore:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, code: str, entry: UrlEntry) -> None:
        model = UrlModel(
            code=code,
            original_url=entry.original_url,
            created_at=entry.created_at,
            expires_at=entry.expires_at
        )
        self.session.add(model)
        await self.session.commit()

    async def get(self, code: str) -> Optional[UrlEntry]:
        result = await self.session.execute(select(UrlModel).where(UrlModel.code == code))
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
            
        if model.expires_at and datetime.now(timezone.utc) > model.expires_at.replace(tzinfo=timezone.utc):
            await self.session.delete(model)
            await self.session.commit()
            return None
            
        return UrlEntry(
            original_url=model.original_url,
            created_at=model.created_at,
            expires_at=model.expires_at
        )

    async def delete(self, code: str) -> bool:
        result = await self.session.execute(select(UrlModel).where(UrlModel.code == code))
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False
