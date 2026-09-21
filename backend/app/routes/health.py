from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.schemas.portfolio import HealthCheckResponse
from app.services.playwright_scraper import scraper_config

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthCheckResponse)
@router.get("/v1/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Lightweight health check endpoint.
    Verifies FastAPI execution and SQLite database connectivity in < 5ms without blocking on Playwright.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "degraded",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        database=db_status,
        playwright="available"
    )

@router.get("/health/detailed", response_model=HealthCheckResponse)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check inspecting Playwright browser engine availability.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    pw_status = await scraper_config.check_playwright_status()

    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "degraded",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        database=db_status,
        playwright=pw_status
    )
