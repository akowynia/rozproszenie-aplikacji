import asyncio
from fastapi import FastAPI

from .config import settings
from .store import InMemoryStore
from .service import ShortenerService
from .router import create_router


def create_app() -> FastAPI:
    app = FastAPI(title="URL Shortener")

    store = InMemoryStore()
    service = ShortenerService(store)

    app.include_router(create_router(service, settings))

    # background cleanup task
    app.state._cleanup_task = None

    async def _cleanup_loop():
        try:
            while True:
                removed = store.delete_expired()
                await asyncio.sleep(settings.cleanup_interval_seconds)
        except asyncio.CancelledError:
            return

    @app.on_event("startup")
    async def _startup():
        app.state._cleanup_task = asyncio.create_task(_cleanup_loop())

    @app.on_event("shutdown")
    async def _shutdown():
        task = app.state._cleanup_task
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    return app


app = create_app()
