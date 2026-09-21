import logging
import math
import re
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, asc, desc
from sqlalchemy.exc import SQLAlchemyError
from app.models.portfolio import PortfolioWebsite
from app.models.analysis import WebsiteAnalysis
from app.schemas.portfolio import PortfolioWebsiteCreate, PortfolioWebsiteUpdate

logger = logging.getLogger("optiinfo_scraper.service")

TARGET_CATEGORIES = [
    "Cargo And Courier Services",
    "Corporate Website",
    "eCommerce Website",
    "Education",
    "Healthcare",
    "Manufacturer Industrial",
    "Others",
    "Real Estate",
    "Religious and Communities",
    "Religious Organization",
    "Travel and Tourism"
]

ALLOWED_SORT_COLUMNS = {
    "id": PortfolioWebsite.id,
    "business_name": PortfolioWebsite.business_name,
    "website_url": PortfolioWebsite.website_url,
    "category": PortfolioWebsite.category,
    "country": PortfolioWebsite.country,
    "status": PortfolioWebsite.status,
    "created_at": PortfolioWebsite.created_at,
    "scraped_at": PortfolioWebsite.scraped_at,
}

def _sanitize_string(val: Optional[str], max_len: int = 255) -> Optional[str]:
    """Sanitize string inputs by stripping whitespace and truncating long values."""
    if not val:
        return None
    cleaned = str(val).strip()
    return cleaned[:max_len] if cleaned else None

def create_portfolio(db: Session, obj_in: Union[PortfolioWebsiteCreate, Dict[str, Any]]) -> PortfolioWebsite:
    """Create a new portfolio website record with transaction rollback handling."""
    data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
    
    data["business_name"] = _sanitize_string(data.get("business_name"), 150) or "Unknown Business"
    data["category"] = _sanitize_string(data.get("category"), 100) or "Others"
    data["country"] = _sanitize_string(data.get("country"), 100)

    try:
        db_obj = PortfolioWebsite(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create portfolio record: {e}")
        raise

def get_portfolios(db: Session, skip: int = 0, limit: int = 100) -> List[PortfolioWebsite]:
    """Retrieve list of portfolio websites."""
    return db.query(PortfolioWebsite).order_by(PortfolioWebsite.id.asc()).offset(skip).limit(limit).all()

def get_portfolio_by_id(db: Session, portfolio_id: int) -> Optional[PortfolioWebsite]:
    """Get portfolio website record by ID."""
    return db.query(PortfolioWebsite).filter(PortfolioWebsite.id == portfolio_id).first()

def get_portfolio_by_url(db: Session, website_url: str) -> Optional[PortfolioWebsite]:
    """Get portfolio website record by unique website URL."""
    if not website_url:
        return None
    sanitized_url = _sanitize_string(website_url, 500)
    return db.query(PortfolioWebsite).filter(PortfolioWebsite.website_url == sanitized_url).first()

def update_portfolio(
    db: Session,
    portfolio_id: int,
    obj_in: Union[PortfolioWebsiteUpdate, Dict[str, Any]]
) -> Optional[PortfolioWebsite]:
    """Update an existing portfolio website record."""
    db_obj = get_portfolio_by_id(db, portfolio_id)
    if not db_obj:
        return None

    update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
    
    try:
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to update portfolio {portfolio_id}: {e}")
        raise

def delete_portfolio(db: Session, portfolio_id: int) -> bool:
    """Delete a portfolio website record and its associated analyses by ID."""
    db_obj = get_portfolio_by_id(db, portfolio_id)
    if not db_obj:
        return False

    try:
        # Delete any associated analysis records
        db.query(WebsiteAnalysis).filter(WebsiteAnalysis.portfolio_id == portfolio_id).delete(synchronize_session=False)
        db.delete(db_obj)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to delete portfolio {portfolio_id}: {e}")
        raise

def upsert_portfolio(
    db: Session,
    obj_in: Union[PortfolioWebsiteCreate, Dict[str, Any]]
) -> PortfolioWebsite:
    """
    Insert or update portfolio record safely.
    Prevents duplicates by checking website_url or business_name + category.
    Handles DB rollbacks cleanly.
    """
    data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
    url = _sanitize_string(data.get("website_url"), 500)
    business_name = _sanitize_string(data.get("business_name"), 150)
    category = _sanitize_string(data.get("category"), 100)

    try:
        existing: Optional[PortfolioWebsite] = None

        if url:
            existing = get_portfolio_by_url(db, url)

        if not existing and business_name and category:
            existing = (
                db.query(PortfolioWebsite)
                .filter(
                    func.lower(PortfolioWebsite.business_name) == business_name.lower(),
                    func.lower(PortfolioWebsite.category) == category.lower()
                )
                .first()
            )

        if existing:
            for field in ["business_name", "category", "country", "status", "source_url", "error_message"]:
                val = data.get(field)
                if val is not None:
                    setattr(existing, field, val)
                    
            if url and not existing.website_url:
                existing.website_url = url

            existing.scraped_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            return create_portfolio(db, data)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to upsert portfolio record ({business_name}): {e}")
        raise

def search_portfolios(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 25,
    sort_by: str = "id",
    sort_order: str = "asc"
) -> Dict[str, Any]:
    """
    Server-side search, category filter, dynamic sorting, and pagination.
    Sanitizes search inputs and handles query errors safely.
    """
    page = max(1, page)
    limit = min(500, max(1, limit))
    offset = (page - 1) * limit

    clean_query = _sanitize_string(query, 100)
    clean_cat = _sanitize_string(category, 100)

    q = db.query(PortfolioWebsite)

    if clean_cat and clean_cat.lower() != "all":
        q = q.filter(func.lower(PortfolioWebsite.category) == clean_cat.lower())

    if clean_query:
        # Escape special SQL wildcard characters in search query
        escaped_query = clean_query.replace("%", "\\%").replace("_", "\\_")
        search_pattern = f"%{escaped_query}%"
        q = q.filter(
            or_(
                PortfolioWebsite.business_name.ilike(search_pattern),
                PortfolioWebsite.website_url.ilike(search_pattern),
                PortfolioWebsite.country.ilike(search_pattern)
            )
        )

    total = q.count()
    pages = math.ceil(total / limit) if limit > 0 else 1

    sort_col = ALLOWED_SORT_COLUMNS.get(sort_by.lower(), PortfolioWebsite.id)
    if sort_order.lower() == "desc":
        q = q.order_by(desc(sort_col))
    else:
        q = q.order_by(asc(sort_col))

    items = q.offset(offset).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

def get_categories_summary(db: Session) -> List[Dict[str, Any]]:
    """Get breakdown of available categories and saved item count per category."""
    counts = (
        db.query(PortfolioWebsite.category, func.count(PortfolioWebsite.id))
        .group_by(PortfolioWebsite.category)
        .all()
    )
    count_dict = {cat: cnt for cat, cnt in counts if cat}

    result = []
    seen = set()
    for cat in TARGET_CATEGORIES:
        cnt = count_dict.get(cat, 0)
        result.append({"name": cat, "count": cnt})
        seen.add(cat.lower())

    for cat, cnt in counts:
        if cat and cat.lower() not in seen:
            result.append({"name": cat, "count": cnt})

    return result

def get_stats(db: Session) -> Dict[str, Any]:
    """Get overall system statistics safely."""
    total_portfolios = db.query(func.count(PortfolioWebsite.id)).scalar() or 0
    total_categories = db.query(func.count(func.distinct(PortfolioWebsite.category))).scalar() or 0
    total_countries = db.query(func.count(func.distinct(PortfolioWebsite.country))).scalar() or 0
    
    last_scraped_at = db.query(func.max(PortfolioWebsite.scraped_at)).scalar()
    categories_summary = get_categories_summary(db)

    return {
        "total_portfolios": total_portfolios,
        "total_categories": total_categories,
        "total_countries": total_countries,
        "last_scraped_at": last_scraped_at,
        "categories_summary": categories_summary
    }
