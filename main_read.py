from fastapi import FastAPI
from app.database import SessionLocal, init_db
from app.store import SqlAlchemyStore
from app.service import ShortenerService
from app.router import create_read_router

app = FastAPI(title="URL Shortener - Read Service")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/{short_code}")
async def redirect(short_code: str):
    async with SessionLocal() as session:
        service = ShortenerService(SqlAlchemyStore(session))
        return await create_read_router(service).redirect(short_code)

@app.get("/api/info/{short_code}")
async def info(short_code: str):
    async with SessionLocal() as session:
        service = ShortenerService(SqlAlchemyStore(session))
        return await create_read_router(service).info(short_code)
