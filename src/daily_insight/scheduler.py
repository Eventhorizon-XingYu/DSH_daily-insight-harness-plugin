"""APScheduler daemon integration for daily article generation."""
from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.blocking import BlockingScheduler


def run_daemon(hour: int, minute: int, timezone: str, job: Callable[[], None]) -> None:
    """Run a blocking cron scheduler and report its next execution."""
    # APScheduler 4.x can leave ``Job.next_run_time`` unset until the scheduler
    # has started.  Calculate the preview from the same trigger used by the job
    # so daemon startup works across supported APScheduler versions.
    zone = ZoneInfo(timezone)
    trigger = CronTrigger(hour=hour, minute=minute, timezone=zone)
    scheduler = BlockingScheduler(timezone=zone)
    scheduler.add_job(job, trigger=trigger)
    next_run = trigger.get_next_fire_time(None, datetime.now(zone))
    print(f"下次执行时间：{next_run}"); logging.info("启动定时守护进程")
    try: scheduler.start()
    except (KeyboardInterrupt, SystemExit): scheduler.shutdown()
