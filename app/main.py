from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import state as st
from app.api.slash import router as slash_router
from app.db import init_db
from app.scheduler import scheduler
from app.services.duty import run_daily_duty


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    s = st.load()
    scheduler.add_job(
        run_daily_duty,
        "cron",
        day_of_week="mon-fri",
        hour=s.post_hour,
        minute=s.post_minute,
        id="daily_duty",
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(slash_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
