from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import admin, auth, favorites, listings, uploads
from app.core.config import settings
from app.services.staleness import run_staleness_check

scheduler = BackgroundScheduler(timezone="America/Toronto")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Daily staleness check at 04:00 Toronto time.
    scheduler.add_job(
        run_staleness_check,
        CronTrigger(hour=4, minute=0),
        id="staleness_check",
        replace_existing=True,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="NestMate API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_base],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve re-hosted images from the media directory.
Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(favorites.router)
app.include_router(uploads.router)
app.include_router(admin.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
