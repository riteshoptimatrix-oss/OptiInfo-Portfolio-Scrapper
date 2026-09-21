from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.portfolio import PortfolioWebsite
from app.models.analysis import WebsiteAnalysis
from app.schemas.analysis import (
    AnalysisResultSchema,
    AnalysisStatusResponse,
    BulkAnalysisRequest,
    BulkAnalysisResponse,
    AnalysisStatsResponse
)
from app.services.analyzer_job_manager import analyzer_job_manager

router = APIRouter(tags=["Website Analysis"])

@router.post("/websites/{portfolio_id}/analyze", response_model=AnalysisStatusResponse)
async def analyze_website_endpoint(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Trigger async website technology analysis for a specific portfolio item.
    """
    portfolio = db.query(PortfolioWebsite).filter(PortfolioWebsite.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio website with ID {portfolio_id} not found.")

    if not portfolio.website_url:
        raise HTTPException(status_code=400, detail="Portfolio item has no valid website URL to analyze.")

    res = await analyzer_job_manager.enqueue_analysis(portfolio.id, portfolio.website_url)
    return AnalysisStatusResponse(**res)

@router.get("/websites/{portfolio_id}/analysis", response_model=AnalysisResultSchema)
def get_website_analysis(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Retrieve latest website analysis result for a portfolio item.
    """
    analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.portfolio_id == portfolio_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis record found for this portfolio website.")

    # Populate primary_technology object for response schema compatibility
    if not hasattr(analysis, "primary_technology") or not analysis.primary_technology:
        name = analysis.primary_technology_name or "HTML / CSS / JavaScript"
        tp = analysis.primary_technology_type or "static"
        conf = analysis.primary_technology_confidence or 90
        ev = analysis.primary_technology_evidence or ["HTML5, CSS, and JS structure detected"]
        
        # Label calculation
        label = "Very High" if conf >= 90 else "High" if conf >= 75 else "Medium" if conf >= 60 else "Low"
        
        analysis.primary_technology = {
            "name": name,
            "type": tp,
            "confidence": conf,
            "confidence_label": label,
            "evidence": ev
        }

    return analysis

@router.get("/websites/{portfolio_id}/analysis/status", response_model=AnalysisStatusResponse)
def get_website_analysis_status(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Check current status of analysis job (queued, analyzing, completed, failed).
    """
    analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.portfolio_id == portfolio_id).first()
    if not analysis:
        return AnalysisStatusResponse(
            portfolio_id=portfolio_id,
            website_url="",
            status="idle"
        )
    return AnalysisStatusResponse(
        portfolio_id=analysis.portfolio_id,
        website_url=analysis.website_url,
        status=analysis.status,
        error=analysis.error_message,
        analyzed_at=analysis.analyzed_at
    )

@router.get("/analyses", response_model=List[AnalysisResultSchema])
def list_analyses(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    List all website analysis records.
    """
    analyses = db.query(WebsiteAnalysis).offset(skip).limit(limit).all()
    return analyses

@router.get("/analyses/{id}", response_model=AnalysisResultSchema)
def get_analysis_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieve specific analysis record by analysis ID.
    """
    analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis record #{id} not found.")
    return analysis

@router.post("/websites/analyze-bulk", response_model=BulkAnalysisResponse)
async def bulk_analyze_websites(req: BulkAnalysisRequest, db: Session = Depends(get_db)):
    """
    Bulk trigger technology analysis for multiple portfolio websites.
    """
    query = db.query(PortfolioWebsite)
    if req.portfolio_ids:
        query = query.filter(PortfolioWebsite.id.in_(req.portfolio_ids))

    portfolios = query.all()
    queued_count = 0

    for p in portfolios:
        if p.website_url:
            await analyzer_job_manager.enqueue_analysis(p.id, p.website_url)
            queued_count += 1

    return BulkAnalysisResponse(
        message=f"Queued {queued_count} portfolio websites for technology analysis.",
        queued_count=queued_count,
        total_requested=len(portfolios)
    )

@router.post("/websites/analyze-stop")
async def stop_bulk_analysis(db: Session = Depends(get_db)):
    """
    Stop all running and queued website technology analysis tasks.
    """
    stopped_count = await analyzer_job_manager.stop_all_jobs()
    return {
        "success": True,
        "message": f"Website analysis stopped successfully. Cancelled {stopped_count} tasks.",
        "stopped_count": stopped_count
    }

@router.get("/analysis/stats", response_model=AnalysisStatsResponse)
def get_analysis_statistics(db: Session = Depends(get_db)):
    """
    Aggregated statistical summary of detected technology stacks across all analyzed websites.
    """
    total_websites = db.query(PortfolioWebsite).count()
    analyzed_count = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.status == "completed").count()
    pending_count = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.status.in_(["queued", "analyzing"])).count()
    failed_count = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.status == "failed").count()

    analyses = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.status == "completed").all()

    cms_counts: dict[str, int] = {}
    framework_counts: dict[str, int] = {}
    hosting_counts: dict[str, int] = {}
    tech_counter: dict[str, int] = {}

    for a in analyses:
        stack = a.technology_stack or {}
        infra = a.infrastructure or {}

        # CMS
        cms = stack.get("cms")
        if cms and cms.get("name"):
            cms_counts[cms["name"]] = cms_counts.get(cms["name"], 0) + 1
            tech_counter[cms["name"]] = tech_counter.get(cms["name"], 0) + 1

        # Frameworks & Frontend
        for f in stack.get("frontend", []):
            if f.get("name"):
                framework_counts[f["name"]] = framework_counts.get(f["name"], 0) + 1
                tech_counter[f["name"]] = tech_counter.get(f["name"], 0) + 1

        # Hosting
        host = infra.get("hosting_provider")
        if host and host.get("name"):
            hosting_counts[host["name"]] = hosting_counts.get(host["name"], 0) + 1

    top_tech = sorted(
        [{"name": k, "count": v} for k, v in tech_counter.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:10]

    return AnalysisStatsResponse(
        total_websites=total_websites,
        analyzed_count=analyzed_count,
        pending_count=pending_count,
        failed_count=failed_count,
        cms_distribution=cms_counts,
        framework_distribution=framework_counts,
        hosting_distribution=hosting_counts,
        top_technologies=top_tech
    )
