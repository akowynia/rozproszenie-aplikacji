from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
from .models import ShortenRequest, ShortenResponse, InfoResponse
from .service import ShortenerService, NotFoundError
from .config import settings

def create_write_router(service: ShortenerService):
    router = APIRouter()

    @router.post("/api/shorten", response_model=ShortenResponse, status_code=201)
    async def shorten(req: ShortenRequest):
        try:
            code, entry = await service.shorten(str(req.url), req.ttl_seconds)
            short_url = f"{settings.base_url.rstrip('/')}/{code}"
            return ShortenResponse(
                short_url=short_url,
                short_code=code,
                original_url=str(entry.original_url),
                expires_at=entry.expires_at,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/api/shorten/{short_code}", status_code=204)
    async def delete(short_code: str):
        if not await service.delete(short_code):
            raise HTTPException(status_code=404, detail="Not found")
        return None

    return router

def create_read_router(service: ShortenerService):
    router = APIRouter()

    @router.get("/{short_code}")
    async def redirect(short_code: str):
        try:
            url = await service.resolve(short_code)
            entry = await service.info(short_code)
            status = 302 if entry.expires_at else 301
            return RedirectResponse(url, status_code=status)
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Not found")

    @router.get("/api/info/{short_code}", response_model=InfoResponse)
    async def info(short_code: str):
        try:
            entry = await service.info(short_code)
            is_expired = False
            if entry.expires_at and entry.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                is_expired = True
            return InfoResponse(
                short_code=short_code,
                original_url=entry.original_url,
                created_at=entry.created_at,
                expires_at=entry.expires_at,
                is_expired=is_expired,
            )
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Not found")

    return router
