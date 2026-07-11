from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.generate import router as generate_router
from app.config import settings
from app.db import init_db
from app.seed import seed_demo_data

app = FastAPI(title="excel-kanri")

app.include_router(auth_router)
app.include_router(generate_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    if settings.demo_mode:
        seed_demo_data()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
