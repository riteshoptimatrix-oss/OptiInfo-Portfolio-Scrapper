import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger("optiinfo_scraper.playwright")

class PlaywrightScraperConfig:
    """
    Playwright Scraper Configuration & Manager.
    Configures browser context and verifies engine availability for scraping OptiInfo Portfolio.
    Actual DOM extraction methods will be implemented in Phase 2.
    """
    TARGET_URL = "https://www.optiinfo.com/our-works/"
    
    def __init__(self):
        self.headless = settings.HEADLESS
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
        self.viewport = {"width": 1280, "height": 800}

    def get_browser_options(self) -> Dict[str, Any]:
        return {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu"
            ]
        }

    async def check_playwright_status(self) -> str:
        """
        Verify if Playwright and browser context can be initialized.
        """
        async def _check():
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                await browser.close()
                return "configured_and_ready"

        try:
            from app.core.async_utils import run_in_proactor_loop
            return await run_in_proactor_loop(_check)
        except Exception as e:
            logger.warning(f"Playwright browser check warning: {repr(e)}", exc_info=True)
            return f"available_with_warning: {repr(e)}"


scraper_config = PlaywrightScraperConfig()
