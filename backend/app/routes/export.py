from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io
import json

from app.core.database import get_db
from app.models.portfolio import PortfolioWebsite
from app.models.analysis import WebsiteAnalysis

router = APIRouter(tags=["Export Data"])

@router.get("/export")
def export_data(
    format: str = Query("excel", description="Format to export: 'excel' or 'json'"),
    db: Session = Depends(get_db)
):
    """
    Export portfolio and analysis data in Excel or JSON format.
    """
    if format not in ["excel", "json"]:
        raise HTTPException(status_code=400, detail="Invalid format requested. Supported formats are 'excel' and 'json'.")

    # Fetch portfolios with their analysis
    results = db.query(PortfolioWebsite, WebsiteAnalysis)\
        .outerjoin(WebsiteAnalysis, PortfolioWebsite.id == WebsiteAnalysis.portfolio_id)\
        .all()

    data_list = []
    for portfolio, analysis in results:
        row = {
            "ID": portfolio.id,
            "Business Name": portfolio.business_name,
            "Website URL": portfolio.website_url,
            "Category": portfolio.category,
            "Country": portfolio.country,
            "Scrape Status": portfolio.status,
            "Scraped At": portfolio.scraped_at.isoformat() if portfolio.scraped_at else None,
        }

        if analysis:
            row.update({
                "Analysis Status": analysis.status,
                "Analyzed At": analysis.analyzed_at.isoformat() if analysis.analyzed_at else None,
                "Page Title": analysis.page_title,
                "HTTP Status": analysis.http_status,
                "Primary Tech Name": analysis.primary_technology_name,
                "Primary Tech Type": analysis.primary_technology_type,
                "Primary Tech Confidence": analysis.primary_technology_confidence,
                "Analyzer Version": analysis.analyzer_version,
                "Overall Confidence": analysis.overall_confidence,
                "Error Message": analysis.error_message or portfolio.error_message
            })
        else:
            row.update({
                "Analysis Status": "Not Analyzed",
                "Analyzed At": None,
                "Page Title": None,
                "HTTP Status": None,
                "Primary Tech Name": None,
                "Primary Tech Type": None,
                "Primary Tech Confidence": None,
                "Analyzer Version": None,
                "Overall Confidence": None,
                "Error Message": portfolio.error_message
            })

        data_list.append(row)

    if format == "json":
        json_data = json.dumps(data_list, indent=4)
        return Response(content=json_data, media_type="application/json", headers={"Content-Disposition": "attachment; filename=export_data.json"})

    elif format == "excel":
        df = pd.DataFrame(data_list)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Analysis Data")
            
        buffer.seek(0)
        return StreamingResponse(
            buffer, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=export_data.xlsx"}
        )
