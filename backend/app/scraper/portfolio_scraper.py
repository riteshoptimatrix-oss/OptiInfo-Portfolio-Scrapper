import logging
from typing import Dict, Any, List, Optional
from app.scraper.browser import BrowserManager
from app.scraper.parser import CardParser
from app.scraper.utils import deduplicate_records

logger = logging.getLogger("optiinfo_scraper.engine")

class OptiInfoPortfolioScraper:
    """
    Production Playwright Scraper for OptiInfo Portfolio (https://www.optiinfo.com/our-works/).
    Directly inspects page DOM, parses cards resiliently, handles missing fields/URLs,
    deduplicates records, and returns standardized output.
    """
    TARGET_URL = "https://www.optiinfo.com/our-works/"

    def __init__(self, headless: bool = True, timeout_ms: int = 45000):
        self.browser_manager = BrowserManager(headless=headless, timeout_ms=timeout_ms)
        self.parser = CardParser()

    async def scrape(self) -> Dict[str, Any]:
        """
        Execute full scraping workflow.
        Returns dictionary with success status, stats, and extracted records list.
        """
        logger.info("Starting OptiInfo Portfolio Scraper execution...")
        records: List[Dict[str, Any]] = []
        total_found = 0
        successful = 0
        failed = 0

        try:
            # 1. Start browser & navigate to target page
            page = await self.browser_manager.navigate_with_retry(self.TARGET_URL)
            
            # 2. Execute DOM extraction script inside page context
            logger.info("Extracting portfolio card elements from DOM...")
            raw_cards = await page.evaluate('''() => {
                // Select all portfolio card items
                const cards = Array.from(document.querySelectorAll('.stm_works .item, .stm_works_wr .item, .item.all'));
                
                return cards.map((card, idx) => {
                    // Business Name
                    const titleEl = card.querySelector('.info .title a') || card.querySelector('.info .title');
                    const businessName = titleEl ? titleEl.innerText : '';

                    // Website URL
                    const siteLinkEl = card.querySelector('.image .siteLink a') || card.querySelector('.info .title a');
                    const websiteUrl = siteLinkEl ? siteLinkEl.getAttribute('href') : null;

                    // Category
                    const categoryEl = card.querySelector('.info .category span') || card.querySelector('.info .category a');
                    const category = categoryEl ? categoryEl.innerText : '';

                    // Country Flag
                    const flagImg = card.querySelector('.info .flagicon img');
                    let country = flagImg ? flagImg.getAttribute('alt') : '';
                    if (!country && flagImg) {
                        const src = flagImg.getAttribute('src') || '';
                        const match = src.match(/flag-([^.]+)\./i);
                        if (match) {
                            country = match[1];
                        }
                    }

                    return {
                        cardIndex: idx + 1,
                        businessName: businessName,
                        websiteUrl: websiteUrl,
                        category: category,
                        country: country
                    };
                });
            }''')

            total_found = len(raw_cards)
            logger.info(f"Detected {total_found} portfolio card elements on page.")

            # 3. Process each card in resilient exception-handling loop
            for idx, raw in enumerate(raw_cards, start=1):
                try:
                    record = self.parser.parse_card_dict(raw, card_index=idx)
                    if record:
                        records.append(record)
                        successful += 1
                    else:
                        failed += 1
                except Exception as card_err:
                    failed += 1
                    logger.error(f"Failed parsing card #{idx}: {str(card_err)}")

            # 4. Deduplicate records
            deduped_records = deduplicate_records(records)
            logger.info(f"Extracted {len(deduped_records)} unique records after deduplication.")

            logger.info(f"Scraper completed successfully: {successful} successful, {failed} failed out of {total_found} total.")

            return {
                "success": True,
                "total_found": total_found,
                "successful": len(deduped_records),
                "failed": failed,
                "records": deduped_records
            }

        except Exception as e:
            logger.error(f"Critical error during portfolio scraping: {str(e)}")
            return {
                "success": False,
                "total_found": total_found,
                "successful": successful,
                "failed": failed,
                "error": str(e),
                "records": []
            }

        finally:
            # 5. Gracefully shutdown browser
            await self.browser_manager.close()
