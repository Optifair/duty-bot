from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import TZ

scheduler = AsyncIOScheduler(timezone=TZ)
