"""
Scheduler implementations for automated workflow execution.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional
import time
import logging
from datetime import datetime, timedelta
import croniter

logger = logging.getLogger(__name__)


class BaseScheduler(ABC):
    """Abstract base for schedulers."""
    
    @abstractmethod
    def should_run(self) -> bool:
        """Check if it's time to run."""
        pass
    
    @abstractmethod
    def wait_until_next(self) -> None:
        """Block until next scheduled run."""
        pass


class IntervalScheduler(BaseScheduler):
    """Run at fixed intervals."""
    
    def __init__(self, interval_seconds: int):
        self.interval = interval_seconds
        self.last_run = time.time()
    
    def should_run(self) -> bool:
        return time.time() - self.last_run >= self.interval
    
    def wait_until_next(self) -> None:
        elapsed = time.time() - self.last_run
        wait_time = max(0, self.interval - elapsed)
        if wait_time > 0:
            logger.info(f"Waiting {wait_time:.1f}s until next run")
            time.sleep(wait_time)
        self.last_run = time.time()


class CronScheduler(BaseScheduler):
    """Run based on cron expression."""
    
    def __init__(self, cron_expr: str, timezone: str = "UTC"):
        self.cron_expr = cron_expr
        self.timezone = timezone
        self.cron = croniter.croniter(cron_expr, datetime.now())
        self.next_run = self.cron.get_next(datetime)
    
    def should_run(self) -> bool:
        return datetime.now() >= self.next_run
    
    def wait_until_next(self) -> None:
        now = datetime.now()
        if now < self.next_run:
            wait_seconds = (self.next_run - now).total_seconds()
            logger.info(f"Waiting until {self.next_run} ({wait_seconds:.1f}s)")
            time.sleep(min(wait_seconds, 1))  # Check every second
        else:
            self.cron = croniter.croniter(self.cron_expr, self.next_run)
            self.next_run = self.cron.get_next(datetime)


class Scheduler:
    """Main scheduler class that runs workflows on schedule."""
    
    def __init__(self, scheduler: BaseScheduler, workflow_fn: Callable):
        self.scheduler = scheduler
        self.workflow_fn = workflow_fn
        self.running = False
        self.run_count = 0
    
    def start(self, blocking: bool = True) -> None:
        """Start the scheduler."""
        self.running = True
        logger.info("Scheduler started")
        
        if blocking:
            self._run_loop()
        else:
            import threading
            thread = threading.Thread(target=self._run_loop, daemon=True)
            thread.start()
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        logger.info(f"Scheduler stopped. Total runs: {self.run_count}")
    
    def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self.running:
            self.scheduler.wait_until_next()
            if not self.running:
                break
            
            try:
                logger.info(f"Running scheduled workflow (run #{self.run_count + 1})")
                self.workflow_fn()
                self.run_count += 1
            except Exception as e:
                logger.error(f"Scheduled run failed: {e}")