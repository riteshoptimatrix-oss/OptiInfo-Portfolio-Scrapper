import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urlunparse

def clean_text(text: Optional[str]) -> str:
    """
    Clean raw text by removing HTML whitespace, newlines, and icon artifacts.
    """
    if not text:
        return ""
    # Collapse multiple whitespace characters into single space
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned

def normalize_url(url: Optional[str]) -> Optional[str]:
    """
    Normalize website URLs by trimming whitespace, adding missing schemes,
    and stripping tracking query parameters.
    """
    if not url:
        return None

    cleaned_url = url.strip()
    if not cleaned_url or cleaned_url in ["#", "javascript:void(0)", "javascript:;"]:
        return None

    # Prepend scheme if missing
    if not cleaned_url.startswith(("http://", "https://")):
        cleaned_url = "https://" + cleaned_url

    try:
        parsed = urlparse(cleaned_url)
        # Reconstruct URL without query string or fragment tracking
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/') or '/',
            '',  # params
            '',  # query (strip tracking)
            ''   # fragment
        ))
        return normalized
    except Exception:
        return cleaned_url

def normalize_country(country: Optional[str]) -> str:
    """
    Normalize country strings to consistent title casing.
    """
    if not country:
        return "Not Specified"

    cleaned = clean_text(country)
    if not cleaned:
        return "Not Specified"

    # Known acronym handling
    upper_countries = {"usa": "USA", "uk": "UK", "uae": "UAE"}
    if cleaned.lower() in upper_countries:
        return upper_countries[cleaned.lower()]

    return cleaned.title()

def deduplicate_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate portfolio records based on unique key (business_name + website_url).
    """
    seen = set()
    deduped = []
    
    for record in records:
        key = (
            record.get("business_name", "").lower(),
            record.get("website_url", "").lower() if record.get("website_url") else ""
        )
        if key not in seen:
            seen.add(key)
            deduped.append(record)
            
    return deduped
