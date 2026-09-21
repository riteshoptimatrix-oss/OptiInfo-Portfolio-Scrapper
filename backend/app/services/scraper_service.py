import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.database import SessionLocal
from app.scraper.portfolio_scraper import OptiInfoPortfolioScraper
from app.services import portfolio_service

logger = logging.getLogger("optiinfo_scraper.scraper_service")

class ScraperJobManager:
    """
    Singleton Manager for background Playwright scraper tasks.
    Enforces a single concurrent job policy, manages live status & progress metrics,
    and bulk upserts scraped records into SQLite.
    """
    _instance: Optional["ScraperJobManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScraperJobManager, cls).__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self._is_running: bool = False
        self._job_id: int = 1
        self.status: str = "idle"  # idle, running, completed, failed
        self.total: int = 0
        self.processed: int = 0
        self.successful: int = 0
        self.failed: int = 0
        self.progress: int = 0  # 0 to 100
        self.error: Optional[str] = None
        self.logs: list[str] = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def is_running(self) -> bool:
        return self._is_running

    def get_status_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "total": self.total,
            "processed": self.processed,
            "successful": self.successful,
            "failed": self.failed,
            "progress": self.progress,
            "error": self.error,
            "logs": self.logs[-100:], # keep only last 100 for payload size
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }

    def _add_log(self, msg: str):
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {msg}"
        self.logs.append(log_entry)
        logger.info(msg)

    async def start_scrape_job(self) -> bool:
        """
        Trigger async background scrape task safely on the main event loop.
        Returns True if task started, or False if job already running.
        """
        if self._is_running:
            logger.warning("Scraper start requested, but job is already running.")
            return False

        # Reset state for new run
        self._is_running = True
        self.status = "running"
        self.total = 0
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.progress = 0
        self.error = None
        self.logs = []
        self.started_at = datetime.utcnow()
        self.completed_at = None

        # Launch background task on running main event loop
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._run_scraper_task())
        task.add_done_callback(self._handle_task_done)

        return True

    def _handle_task_done(self, task: asyncio.Task):
        """
        Callback for asyncio task completion to retrieve and log exceptions safely.
        Prevents 'Task exception was never retrieved' warnings.
        """
        try:
            exc = task.exception()
            if exc:
                logger.error(f"Background scraper task finished with error: {exc}")
        except asyncio.CancelledError:
            logger.info("Background scraper task was cancelled.")
        except Exception as err:
            logger.error(f"Error checking task exception state: {err}")


    async def _run_scraper_task(self):
        """
        Asynchronous background task executing Playwright scraping and SQLite upserts.
        """
        self._add_log("Background scraper task initiated.")
        self._add_log("Launching headless Playwright browser...")
        db = SessionLocal()
        try:
            from app.core.async_utils import run_in_proactor_loop
            scraper = OptiInfoPortfolioScraper(headless=True)
            result = await run_in_proactor_loop(scraper.scrape)

            if not result.get("success"):
                self.status = "failed"
                self.error = result.get("error", "Unknown Playwright scraper error")
                self.completed_at = datetime.utcnow()
                self._add_log(f"Scraper failed: {self.error}")
                return

            records = result.get("records", [])
            self.total = result.get("total_found", len(records))
            self.failed = result.get("failed", 0)
            self._add_log(f"Successfully scraped {self.total} portfolio URLs.")
            self._add_log("Starting database batch upsert process...")

            # Upsert extracted records into SQLite with live progress updates
            for idx, record in enumerate(records, start=1):
                try:
                    portfolio_service.upsert_portfolio(db, record)
                    self.successful += 1
                except Exception as db_err:
                    self.failed += 1
                    self._add_log(f"Error saving record {idx} to database.")

                self.processed = idx
                if self.total > 0:
                    self.progress = min(100, int((self.processed / self.total) * 100))

            self.status = "completed"
            self.progress = 100
            self.completed_at = datetime.utcnow()
            self._add_log(f"Job completed. {self.successful} records successfully saved to DB.")

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            self.completed_at = datetime.utcnow()
            self._add_log(f"Unhandled exception during execution: {str(e)}")
        finally:
            self._is_running = False
            db.close()

scraper_job_manager = ScraperJobManager()
