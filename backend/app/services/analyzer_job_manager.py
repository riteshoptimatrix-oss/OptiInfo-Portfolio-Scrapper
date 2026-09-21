import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.portfolio import PortfolioWebsite
from app.models.analysis import WebsiteAnalysis
from app.analyzer.analyzer_service import analyzer_pipeline

logger = logging.getLogger("optiinfo_scraper.analyzer_job_manager")

MAX_CONCURRENCY = 3
MAX_RETRIES = 2

class AnalyzerJobManager:
    """
    Async Queue Manager for Background Website Analysis Tasks.
    Enforces MAX_ANALYSIS_CONCURRENCY=3, manages queue states, handles retries,
    and updates SQLite analysis records asynchronously.
    """
    _instance: Optional["AnalyzerJobManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalyzerJobManager, cls).__new__(cls)
            cls._instance._init_semaphore()
        return cls._instance

    def _init_semaphore(self):
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
        self._active_jobs: Dict[int, str] = {}  # portfolio_id -> status
        self._running_tasks: Dict[int, asyncio.Task] = {}

    async def stop_all_jobs(self) -> int:
        """
        Cancels all running background analysis tasks and updates queued/analyzing DB records.
        """
        stopped_count = 0
        # Cancel all active tasks
        for portfolio_id, task in list(self._running_tasks.items()):
            if not task.done():
                task.cancel()
                stopped_count += 1
        self._running_tasks.clear()

        # Update database records in status 'queued' or 'analyzing'
        db: Session = SessionLocal()
        try:
            active_records = db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.status.in_(["queued", "analyzing"])
            ).all()
            for record in active_records:
                record.status = "failed"
                record.error_message = "Analysis manually stopped by user"
                stopped_count += 1
            db.commit()
        except Exception as e:
            logger.error(f"Error marking analysis jobs as stopped in DB: {e}")
        finally:
            db.close()

        logger.info(f"[JOB MANAGER] Stopped {stopped_count} analysis tasks.")
        return stopped_count

    async def enqueue_analysis(self, portfolio_id: int, website_url: str) -> Dict[str, Any]:
        """
        Enqueues a website for analysis without blocking the HTTP request thread.
        """
        db: Session = SessionLocal()
        try:
            # Check existing analysis record
            analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.portfolio_id == portfolio_id).first()
            if not analysis:
                analysis = WebsiteAnalysis(
                    portfolio_id=portfolio_id,
                    website_url=website_url,
                    status="queued"
                )
                db.add(analysis)
            else:
                analysis.status = "queued"
                analysis.error_message = None

            db.commit()
            db.refresh(analysis)

            # Spawn background task on main event loop
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._process_analysis_job(portfolio_id, website_url))
            self._running_tasks[portfolio_id] = task

            return {
                "portfolio_id": portfolio_id,
                "website_url": website_url,
                "status": "queued"
            }

        finally:
            db.close()

    async def _process_analysis_job(self, portfolio_id: int, website_url: str):
        """
        Worker task governed by concurrency semaphore and retry handling.
        """
        async with self._semaphore:
            logger.info(f"[JOB MANAGER] Starting analysis for portfolio ID {portfolio_id} ({website_url})")
            db: Session = SessionLocal()

            try:
                # Update status to analyzing
                analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.portfolio_id == portfolio_id).first()
                if analysis:
                    analysis.status = "analyzing"
                    db.commit()

                # Execute pipeline with retry loop
                result = None
                for attempt in range(1, MAX_RETRIES + 2):
                    logger.info(f"Analysis attempt {attempt} for {website_url}...")
                    result = await analyzer_pipeline.analyze_website(website_url)
                    if result.get("success"):
                        break
                    if attempt <= MAX_RETRIES:
                        await asyncio.sleep(2 * attempt)

                analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.portfolio_id == portfolio_id).first()
                if not analysis:
                    return

                if result.get("success"):
                    pt = result.get("primary_technology", {})
                    analysis.status = "completed"
                    analysis.analyzed_at = datetime.utcnow()
                    analysis.page_title = result.get("page_title")
                    analysis.final_url = result.get("final_url")
                    analysis.http_status = result.get("http_status")
                    analysis.primary_technology_name = pt.get("name")
                    analysis.primary_technology_type = pt.get("type")
                    analysis.primary_technology_confidence = pt.get("confidence", 0)
                    analysis.primary_technology_evidence = pt.get("evidence")
                    analysis.analyzer_version = result.get("analyzer_version", "2.0.0")
                    analysis.technology_stack = result.get("technology_stack")
                    analysis.infrastructure = result.get("infrastructure")
                    analysis.analytics = result.get("analytics")
                    analysis.integrations = result.get("integrations")
                    analysis.metadata_info = result.get("metadata_info")
                    analysis.performance_metrics = result.get("performance_metrics")
                    analysis.evidence = result.get("evidence")
                    analysis.overall_confidence = result.get("overall_confidence", 80)
                    analysis.error_message = None
                    logger.info(f"[JOB MANAGER] Successfully completed analysis for portfolio ID {portfolio_id}")

                else:
                    analysis.status = "failed"
                    analysis.error_message = result.get("error", "Analysis failed after retries")
                    logger.error(f"[JOB MANAGER] Analysis failed for portfolio ID {portfolio_id}: {analysis.error_message}")

                db.commit()

            except Exception as e:
                logger.error(f"Critical worker error processing portfolio ID {portfolio_id}: {str(e)}")
                analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.portfolio_id == portfolio_id).first()
                if analysis:
                    analysis.status = "failed"
                    analysis.error_message = str(e)
                    db.commit()

            finally:
                self._running_tasks.pop(portfolio_id, None)
                db.close()

analyzer_job_manager = AnalyzerJobManager()
