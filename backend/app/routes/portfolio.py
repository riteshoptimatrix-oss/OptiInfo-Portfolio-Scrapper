from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.portfolio import (
    PortfolioWebsiteResponse,
    PortfolioPaginatedResponse,
    PortfolioWebsiteCreate
)
from app.schemas.scraper import CategorySummary, StatsResponse
from app.services import portfolio_service

router = APIRouter(tags=["Portfolios"])

@router.get("/portfolios", response_model=PortfolioPaginatedResponse)
def get_portfolios(
    search: Optional[str] = Query(None, description="Search by business name, URL, or country"),
    category: Optional[str] = Query(None, description="Filter by business category"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(25, ge=1, le=500, description="Page size limit"),
    sort_by: str = Query("id", description="Column to sort by (id, business_name, category, country, created_at)"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    """
    List and search portfolio website records with server-side pagination, category filtering, search, and sorting.
    """
    result = portfolio_service.search_portfolios(
        db=db,
        query=search,
        category=category,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return result

@router.get("/portfolios/{portfolio_id}", response_model=PortfolioWebsiteResponse)
def get_portfolio_by_id(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Get a single portfolio website record by ID.
    """
    item = portfolio_service.get_portfolio_by_id(db, portfolio_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio record with ID {portfolio_id} not found."
        )
    return item

@router.delete("/portfolios/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_by_id(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Delete a portfolio website record by ID.
    """
    deleted = portfolio_service.delete_portfolio(db, portfolio_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio record with ID {portfolio_id} not found."
        )
    return None

@router.get("/categories", response_model=List[CategorySummary])
def get_categories(db: Session = Depends(get_db)):
    """
    Get list of available portfolio categories with saved item counts.
    """
    return portfolio_service.get_categories_summary(db)

@router.get("/stats", response_model=StatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get overall system stats (totals, unique categories, countries, last_scraped_at, category breakdown).
    """
    return portfolio_service.get_stats(db)
