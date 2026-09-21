from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class ScrapeStartResponse(BaseModel):
    message: str
    status: str
    job_id: int

class ScrapeStatusResponse(BaseModel):
    status: str  # "idle", "running", "completed", "failed"
    total: int
    processed: int
    successful: int
    failed: int
    progress: int  # 0 to 100 percentage
    error: Optional[str] = None
    logs: List[str] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class CategorySummary(BaseModel):
    name: str
    count: int

class StatsResponse(BaseModel):
    total_portfolios: int
    total_categories: int
    total_countries: int
    last_scraped_at: Optional[datetime] = None
    categories_summary: List[CategorySummary]
