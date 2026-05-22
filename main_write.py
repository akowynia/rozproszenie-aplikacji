from fastapi import FastAPI
from app.database import init_db, shutdown_db, get_session
from app.store import CassandraStore
from app.service import ShortenerService
from app.router import create_write_router
from app.models import ShortenRequest

app = FastAPI(title="URL Shortener - Write Service")

@app.on_event("startup")
def startup():
    init_db()

@app.on_event("shutdown")
def shutdown():
    shutdown_db()

@app.post("/api/shorten", status_code=201)
async def shorten(req: ShortenRequest):
    session = get_session()
    service = ShortenerService(CassandraStore(session))
    return await create_write_router(service).shorten(req)

@app.delete("/api/shorten/{short_code}", status_code=204)
async def delete(short_code: str):
    session = get_session()
    service = ShortenerService(CassandraStore(session))
    return await create_write_router(service).delete(short_code)
