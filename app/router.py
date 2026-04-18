from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

from .models import ShortenRequest, ShortenResponse, InfoResponse

router = APIRouter()


def create_router(service, settings):
    @router.post("/api/shorten", response_model=ShortenResponse, status_code=201)
    async def shorten(req: ShortenRequest):
        try:
            code, entry = service.shorten(str(req.url), req.ttl_seconds)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        short_url = f"{settings.base_url.rstrip('/')}/{code}"
        return ShortenResponse(
            short_url=short_url,
            short_code=code,
            original_url=str(entry.original_url),
            expires_at=entry.expires_at,
        )

    @router.get("/{short_code}")
    async def redirect(short_code: str):
        try:
            url = service.resolve(short_code)
        except Exception:
            raise HTTPException(status_code=404, detail="Not found")
        # if there is an expires_at we use 302, otherwise 301
        entry = service.info(short_code)
        if entry.expires_at is None:
            return RedirectResponse(url, status_code=301)
        return RedirectResponse(url, status_code=302)

    @router.get("/api/info/{short_code}", response_model=InfoResponse)
    async def info(short_code: str):
        try:
            entry = service.info(short_code)
        except Exception:
            raise HTTPException(status_code=404, detail="Not found")
        is_expired = False
        if entry.expires_at and entry.expires_at < datetime.now(timezone.utc):
            is_expired = True
        return InfoResponse(
            short_code=short_code,
            original_url=entry.original_url,
            created_at=entry.created_at,
            expires_at=entry.expires_at,
            is_expired=is_expired,
        )

    @router.delete("/api/shorten/{short_code}", status_code=204)
    async def delete(short_code: str):
        # simple deletion via store access
        if service.store.get(short_code) is None:
            raise HTTPException(status_code=404, detail="Not found")
        del service.store._data[short_code]
        return None

    return router
