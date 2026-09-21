from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class PortfolioWebsiteBase(BaseModel):
    business_name: str
    website_url: Optional[str] = None
    category: str
    country: Optional[str] = None
    source_url: Optional[str] = "https://www.optiinfo.com/our-works/"
    status: Optional[str] = "scraped"
    error_message: Optional[str] = None

class PortfolioWebsiteCreate(PortfolioWebsiteBase):
    pass

class PortfolioWebsiteUpdate(BaseModel):
    business_name: Optional[str] = None
    website_url: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    scraped_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None

class PortfolioWebsiteResponse(PortfolioWebsiteBase):
    id: int
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime
    last_checked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PortfolioPaginatedResponse(BaseModel):
    items: List[PortfolioWebsiteResponse]
    total: int
    page: int
    limit: int
    pages: int

class ScrapeJobResponse(BaseModel):
    id: int
    status: str
    total_found: int
    scraped_count: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    version: str
    database: str
    playwright: str
