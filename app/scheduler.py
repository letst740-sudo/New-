from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.services import weather as W, rates as R, movies as M

scheduler = AsyncIOScheduler(timezone=settings.tz)

def setup_jobs():
    scheduler.add_job(W.fetch_weather, CronTrigger(minute=0, hour="*/2"))
    scheduler.add_job(R.fetch_fiat, CronTrigger(minute="*/5"))
    scheduler.add_job(R.fetch_crypto, CronTrigger(minute="*/5"))
    scheduler.add_job(M.fetch_movies, CronTrigger(minute=5))
