"""
DelayRay Background Job Scheduler & Orchestration
Integrates APScheduler for scheduled monthly monitoring cycles and asynchronous tasks.
Adheres strictly to docs/BUILD_SPEC.md Section 2 and 9.
"""

import logging
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.app.db.session import SessionLocal
from backend.app.ews.engine import EWSEngine

logger = logging.getLogger("delayray.jobs")

scheduler = BackgroundScheduler()

def run_monthly_scoring_job():
    """
    Scheduled job: rescores ongoing project snapshots and evaluates EWS rules.
    """
    logger.info("Executing scheduled monthly portfolio scoring and alert check...")
    db = SessionLocal()
    try:
        engine = EWSEngine(db)
        new_alerts = engine.evaluate_portfolio(limit=200)
        logger.info(f"Scheduled scoring cycle complete: {len(new_alerts)} new alerts evaluated.")
    except Exception as e:
        logger.error(f"Error in monthly scoring job: {e}")
    finally:
        db.close()

def start_scheduler():
    """Starts the APScheduler background daemon if not already running."""
    if not scheduler.running:
        # Schedule on 1st of every month at 02:00 AM
        scheduler.add_job(
            run_monthly_scoring_job,
            trigger=CronTrigger(day=1, hour=2, minute=0),
            id="monthly_scoring_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info("DelayRay APScheduler started.")

def shutdown_scheduler():
    """Gracefully stops background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("DelayRay APScheduler shut down.")
