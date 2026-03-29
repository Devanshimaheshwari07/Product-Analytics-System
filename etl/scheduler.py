"""
Scheduler — APScheduler-based cron job for automated ETL execution.
Runs incremental pipeline every hour and full refresh daily at midnight.
"""
import os
import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from pipeline import run_incremental_pipeline, run_full_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCHEDULE_HOURS = int(os.getenv("ETL_SCHEDULE_HOURS", "1"))
FULL_REFRESH_HOUR = int(os.getenv("ETL_FULL_REFRESH_HOUR", "0"))


def main():
    logger.info("=" * 60)
    logger.info("ETL Scheduler starting...")
    logger.info(f"  Incremental: every {SCHEDULE_HOURS} hour(s)")
    logger.info(f"  Full refresh: daily at {FULL_REFRESH_HOUR:02d}:00")
    logger.info("=" * 60)

    # Run initial full pipeline on startup (wait for DB to be ready)
    logger.info("Running initial full pipeline on startup...")
    retry_count = 0
    max_retries = 10

    while retry_count < max_retries:
        try:
            run_full_pipeline()
            logger.info("Initial pipeline completed successfully")
            break
        except Exception as e:
            retry_count += 1
            logger.warning(
                f"Initial pipeline attempt {retry_count}/{max_retries} failed: {e}"
            )
            if retry_count < max_retries:
                time.sleep(10)
            else:
                logger.error("Max retries reached for initial pipeline. Continuing with scheduler...")

    # Set up the scheduler
    scheduler = BlockingScheduler()

    # Incremental pipeline — runs every N hours
    scheduler.add_job(
        run_incremental_pipeline,
        trigger=IntervalTrigger(hours=SCHEDULE_HOURS),
        id="incremental_etl",
        name="Incremental ETL Pipeline",
        max_instances=1,
        replace_existing=True,
    )

    # Full refresh — runs daily at midnight
    scheduler.add_job(
        run_full_pipeline,
        trigger=CronTrigger(hour=FULL_REFRESH_HOUR, minute=0),
        id="full_etl",
        name="Full ETL Pipeline Refresh",
        max_instances=1,
        replace_existing=True,
    )

    logger.info("Scheduler configured. Starting...")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
