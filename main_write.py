from fastapi import FastAPI
from app.database import SessionLocal, init_db
from app.store import SqlAlchemyStore
from app.service import ShortenerService
from app.router import create_write_router
from app.models import ShortenRequest

app = FastAPI(title="URL Shortener - Write Service")

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/api/shorten", status_code=201)
async def shorten(req: ShortenRequest):
    async with SessionLocal() as session:
        service = ShortenerService(SqlAlchemyStore(session))
        return await create_write_router(service).shorten(req)

@app.delete("/api/shorten/{short_code}", status_code=204)
async def delete(short_code: str):
    async with SessionLocal() as session:
        service = ShortenerService(SqlAlchemyStore(session))
        return await create_write_router(service).delete(short_code)
