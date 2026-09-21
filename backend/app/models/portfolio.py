from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class PortfolioWebsite(Base):
    __tablename__ = "portfolio_websites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_name = Column(String(255), nullable=False, index=True)
    website_url = Column(String(500), nullable=True, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=True, index=True)
    source_url = Column(String(500), default="https://www.optiinfo.com/our-works/")
    status = Column(String(50), default="scraped", index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)

    analyses = relationship("WebsiteAnalysis", back_populates="portfolio", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        Index("idx_website_url_category", "website_url", "category"),
        Index("idx_business_name_category", "business_name", "category"),
    )

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(String(50), default="idle", index=True)  # idle, running, completed, failed
    total_found = Column(Integer, default=0)
    scraped_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
