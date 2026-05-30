from fastapi import FastAPI, HTTPException
from app.database import init_db, shutdown_db, get_session
from app.store import CassandraStore
from app.service import ShortenerService
from app.models import ShortenRequest, ShortenResponse
from app.config import settings

app = FastAPI(title="URL Shortener - Write Service")

@app.on_event("startup")
def startup():
    init_db()

@app.on_event("shutdown")
def shutdown():
    shutdown_db()

@app.post("/api/shorten", response_model=ShortenResponse, status_code=201)
async def shorten(req: ShortenRequest):
    session = get_session()
    service = ShortenerService(CassandraStore(session))
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

@app.delete("/api/shorten/{short_code}", status_code=204)
async def delete(short_code: str):
    session = get_session()
    service = ShortenerService(CassandraStore(session))
    if not await service.delete(short_code):
        raise HTTPException(status_code=404, detail="Not found")
    return None
