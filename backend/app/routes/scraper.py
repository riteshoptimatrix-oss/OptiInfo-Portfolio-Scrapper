from fastapi import APIRouter, HTTPException, status
from app.schemas.scraper import ScrapeStartResponse, ScrapeStatusResponse
from app.services.scraper_service import scraper_job_manager

router = APIRouter(prefix="/scrape", tags=["Scraper"])

@router.post("/start", response_model=ScrapeStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_scrape_job():
    """
    Trigger Playwright scraper background job.
    Returns HTTP 202 Accepted if started, or HTTP 409 Conflict if already running.
    """
    started = await scraper_job_manager.start_scrape_job()
    if not started:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A portfolio scrape job is already in progress."
        )

    return ScrapeStartResponse(
        message="Portfolio scraper job started in background.",
        status="running",
        job_id=1
    )

@router.get("/status", response_model=ScrapeStatusResponse)
async def get_scrape_job_status():
    """
    Get live progress status of the Playwright scraper engine.
    """
    return scraper_job_manager.get_status_dict()

