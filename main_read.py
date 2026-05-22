from fastapi import FastAPI
from app.database import init_db, shutdown_db, get_session
from app.store import CassandraStore
from app.service import ShortenerService
from app.router import create_read_router

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
    return await create_read_router(service).redirect(short_code)

@app.get("/api/info/{short_code}")
async def info(short_code: str):
    session = get_session()
    service = ShortenerService(CassandraStore(session))
    return await create_read_router(service).info(short_code)
