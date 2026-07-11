import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.files import router as files_router
from app.api.generate import router as generate_router
from app.api.pdf import router as pdf_router
from app.api.search import router as search_router
from app.config import settings
from app.db import init_db
from app.seed import seed_demo_data
from app.watcher import watch_shared

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    if settings.demo_mode:
        seed_demo_data()

    shared_dir = Path(settings.shared_dir)
    if shared_dir.is_dir():
        with watch_shared(shared_dir):
            yield
    else:
        logger.warning("shared_dir が存在しないため、shared/ の監視をスキップします: %s", shared_dir)
        yield


app = FastAPI(title="excel-kanri", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(generate_router)
app.include_router(files_router)
app.include_router(pdf_router)
app.include_router(search_router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
