from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class WebsiteAnalysis(Base):
    __tablename__ = "website_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio_websites.id", ondelete="CASCADE"), nullable=False, index=True)
    website_url = Column(String(500), nullable=False, index=True)
    status = Column(String(50), default="queued", index=True)  # queued, analyzing, completed, failed
    analyzed_at = Column(DateTime, nullable=True)

    page_title = Column(String(500), nullable=True)
    final_url = Column(String(500), nullable=True)
    http_status = Column(Integer, nullable=True)

    # Dedicated Primary Technology Classification fields
    primary_technology_name = Column(String(200), nullable=True, index=True)
    primary_technology_type = Column(String(100), nullable=True, index=True) # cms, ecommerce, framework, static
    primary_technology_confidence = Column(Integer, default=0)
    primary_technology_evidence = Column(JSON, nullable=True)
    analyzer_version = Column(String(20), default="2.0.0", index=True)

    technology_stack = Column(JSON, nullable=True)
    infrastructure = Column(JSON, nullable=True)
    analytics = Column(JSON, nullable=True)
    integrations = Column(JSON, nullable=True)
    metadata_info = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)

    overall_confidence = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    portfolio = relationship("PortfolioWebsite", back_populates="analyses")

    __table_args__ = (
        Index("idx_analysis_portfolio_status", "portfolio_id", "status"),
        Index("idx_analysis_url_status", "website_url", "status"),
    )
