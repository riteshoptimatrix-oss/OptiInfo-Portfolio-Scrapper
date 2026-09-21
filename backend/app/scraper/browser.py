import sys
import asyncio
import logging
from typing import Optional

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from app.core.config import settings


logger = logging.getLogger("optiinfo_scraper.browser")

class BrowserManager:
    """
    Async Playwright Browser Manager.
    Handles Chromium lifecycle, navigation retries, configurable timeouts,
    user-agent configuration, and graceful cleanup.
    """
    def __init__(
        self,
        headless: Optional[bool] = None,
        timeout_ms: int = 45000,
        max_retries: int = 3
    ):
        self.headless = headless if headless is not None else settings.PLAYWRIGHT_HEADLESS
        self.timeout_ms = timeout_ms
        self.max_retries = max_retries
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
        
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def start(self) -> Page:
        """
        Launch Chromium browser instance and open a new page context.
        """
        logger.info(f"Starting Playwright Chromium browser (headless={self.headless})...")
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu"
                ]
            )
            self._context = await self._browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 1440, "height": 900}
            )
            self._context.set_default_timeout(self.timeout_ms)
            self._page = await self._context.new_page()
            logger.info("Playwright browser instance started successfully.")
            return self._page
        except Exception as e:
            logger.error(f"Failed to start Playwright browser: {str(e)}")
            await self.close()
            raise

    async def navigate_with_retry(self, url: str, wait_until: str = "domcontentloaded") -> Page:
        """
        Navigate to target URL with automated retry logic and exponential backoff.
        """
        if not self._page:
            await self.start()

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Navigating to {url} (Attempt {attempt}/{self.max_retries})...")
                response = await self._page.goto(url, wait_until=wait_until, timeout=self.timeout_ms)
                status = response.status if response else "Unknown"
                logger.info(f"Page loaded successfully with status code {status}.")
                await self._page.wait_for_timeout(2000)
                return self._page
            except Exception as e:
                logger.warning(f"Navigation attempt {attempt} failed: {str(e)}")
                if attempt == self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) reached for {url}.")
                    raise
                await asyncio.sleep(2 * attempt)

        return self._page

    async def close(self):
        """
        Gracefully close page, context, browser, and Playwright process.
        """
        logger.info("Initiating graceful browser shutdown...")
        try:
            if self._page and not self._page.is_closed():
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("Browser shut down cleanly.")
        except Exception as e:
            logger.warning(f"Error during browser shutdown: {str(e)}")
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
