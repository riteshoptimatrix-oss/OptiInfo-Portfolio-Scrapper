import logging
from typing import Dict, Any, Optional
from app.scraper.utils import clean_text, normalize_url, normalize_country

logger = logging.getLogger("optiinfo_scraper.parser")

class CardParser:
    """
    Parser for extracting structured portfolio card data from DOM.
    Extracts business_name, website_url, category, and country using robust CSS selectors
    and multiple fallback strategies.
    """

    @staticmethod
    def parse_card_dict(raw: Dict[str, Any], card_index: int = 0) -> Optional[Dict[str, Any]]:
        """
        Parse raw card evaluation dictionary extracted from Playwright evaluate page context.
        """
        try:
            # 1. Business Name Extraction & Cleaning
            business_name = clean_text(raw.get("businessName", ""))
            if not business_name:
                logger.warning(f"Card #{card_index}: Business Name missing or empty.")
                return None

            # 2. Website URL Extraction & Normalization
            raw_url = raw.get("websiteUrl")
            website_url = normalize_url(raw_url)
            if not website_url and raw_url:
                logger.warning(f"Card #{card_index} ({business_name}): Invalid URL format '{raw_url}'.")

            # 3. Category Extraction
            category = clean_text(raw.get("category", ""))
            if not category:
                logger.warning(f"Card #{card_index} ({business_name}): Category missing.")
                category = "Others"

            # 4. Country Extraction & Normalization
            country = normalize_country(raw.get("country"))

            record = {
                "business_name": business_name,
                "website_url": website_url,
                "category": category,
                "country": country
            }

            return record

        except Exception as e:
            logger.error(f"Card #{card_index}: Unexpected exception during card parsing: {str(e)}")
            return None
