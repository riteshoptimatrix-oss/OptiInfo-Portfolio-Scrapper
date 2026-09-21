from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class PrimaryTechnologySchema(BaseModel):
    name: str
    type: str  # cms, ecommerce, framework, static
    confidence: int
    confidence_label: str  # Very High, High, Medium, Low
    evidence: List[str] = []

class TechItemSchema(BaseModel):
    name: str
    category: str
    confidence: int
    confidence_label: Optional[str] = "High"
    evidence: List[str] = []

class InfrastructureItemSchema(BaseModel):
    name: str
    confidence: int
    evidence: List[str] = []
    reason: Optional[str] = None

class AnalysisResultSchema(BaseModel):
    id: int
    portfolio_id: int
    website_url: str
    status: str
    analyzed_at: Optional[datetime] = None
    page_title: Optional[str] = None
    final_url: Optional[str] = None
    http_status: Optional[int] = None

    # Primary Technology Classification
    primary_technology_name: Optional[str] = None
    primary_technology_type: Optional[str] = None
    primary_technology_confidence: Optional[int] = 0
    primary_technology_evidence: Optional[List[str]] = None
    primary_technology: Optional[Dict[str, Any]] = None
    analyzer_version: Optional[str] = "2.0.0"

    technology_stack: Optional[Dict[str, Any]] = None
    infrastructure: Optional[Dict[str, Any]] = None
    analytics: Optional[List[Dict[str, Any]]] = None
    integrations: Optional[List[Dict[str, Any]]] = None
    metadata_info: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    overall_confidence: int = 0
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AnalysisStatusResponse(BaseModel):
    portfolio_id: int
    website_url: str
    status: str
    error: Optional[str] = None
    analyzed_at: Optional[datetime] = None

class BulkAnalysisRequest(BaseModel):
    portfolio_ids: Optional[List[int]] = None  # If None, analyzes all portfolios without analysis

class BulkAnalysisResponse(BaseModel):
    message: str
    queued_count: int
    total_requested: int

class AnalysisStatsResponse(BaseModel):
    total_websites: int
    analyzed_count: int
    pending_count: int
    failed_count: int
    cms_distribution: Dict[str, int]
    framework_distribution: Dict[str, int]
    hosting_distribution: Dict[str, int]
    top_technologies: List[Dict[str, Any]]
