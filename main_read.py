from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
from app.database import init_db, shutdown_db, get_session
from app.store import CassandraStore
from app.service import ShortenerService, NotFoundError
from app.models import InfoResponse

app = FastAPI(title="URL Shortener - Read Service")

@app.on_event("startup")
def startup():
    init_db()

@app.on_event("shutdown")
def shutdown():
    shutdown_db()

@app.get("/{short_code}")
async def redirect(short_code: str):
    session = get_session()
    service = ShortenerService(CassandraStore(session))
    try:
        url = await service.resolve(short_code)
        entry = await service.info(short_code)
        status = 302 if entry.expires_at else 301
        return RedirectResponse(url, status_code=status)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Not found")

@app.get("/api/info/{short_code}", response_model=InfoResponse)
async def info(short_code: str):
    session = get_session()
    service = ShortenerService(CassandraStore(session))
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
