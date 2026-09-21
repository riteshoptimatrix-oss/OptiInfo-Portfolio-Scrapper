import asyncio
import logging
from typing import Dict, Any, List
from playwright.async_api import async_playwright
from app.core.config import settings
from app.core.async_utils import run_in_proactor_loop

logger = logging.getLogger("optiinfo_scraper.browser_analyzer")

async def analyze_website_with_playwright(url: str, timeout_ms: int = 12000) -> Dict[str, Any]:
    """
    Launches headless Playwright Chromium to inspect page DOM, loaded scripts, stylesheets,
    meta tags, images, iframe sources, and custom framework markers.
    """
    async def _inspect():
        logger.info(f"Launching Playwright Chromium to inspect {url}...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=settings.HEADLESS,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu"
                    ]
                )
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1440, "height": 900}
                )
                context.set_default_timeout(timeout_ms)
                page = await context.new_page()

                headers_captured = {}
                # Capture response headers from main document navigation
                def handle_response(response):
                    if response.url == page.url or response.url == url:
                        for k, v in response.headers.items():
                            headers_captured[k.lower()] = v

                page.on("response", handle_response)

                try:
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                    try:
                        await page.wait_for_timeout(1000) # Allow dynamic scripts to settle
                    except Exception:
                        pass

                    status_code = response.status if response else 0
                    final_url = page.url
                    page_title = await page.title()
                    html_content = await page.content()

                    # Extract assets and DOM markers in single evaluate call
                    dom_inspection = await page.evaluate('''() => {
                        const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
                        const inlineScripts = Array.from(document.querySelectorAll('script:not([src])')).map(s => s.innerText.slice(0, 300));
                        const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href);
                        const images = Array.from(document.querySelectorAll('img[src]')).map(i => i.src);
                        const iframes = Array.from(document.querySelectorAll('iframe[src]')).map(f => f.src);

                        const metaTags = Array.from(document.querySelectorAll('meta')).map(m => {
                            return {
                                name: m.getAttribute('name') || '',
                                property: m.getAttribute('property') || '',
                                content: m.getAttribute('content') || ''
                            };
                        });

                        // Framework DOM markers
                        const hasNextData = !!document.getElementById('__NEXT_DATA__');
                        const hasReactRoot = !!document.querySelector('[data-reactroot]') || !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
                        const hasNuxtData = !!window.__NUXT__;
                        const hasVueAttr = !!document.querySelector('[data-v-]') || !!document.querySelector('[v-data]');
                        const hasAngular = !!document.querySelector('[ng-version]') || !!document.querySelector('[ng-app]');

                        return {
                            scripts: scripts.concat(inlineScripts),
                            stylesheets: stylesheets,
                            images: images,
                            iframes: iframes,
                            metaTags: metaTags,
                            domInfo: {
                                has_next_data: hasNextData,
                                has_react_root: hasReactRoot,
                                has_nuxt_data: hasNuxtData,
                                has_vue_attr: hasVueAttr,
                                has_angular: hasAngular
                            }
                        };
                    }''')

                    return {
                        "success": True,
                        "status_code": status_code,
                        "final_url": final_url,
                        "page_title": page_title,
                        "html": html_content,
                        "headers": headers_captured,
                        "scripts": dom_inspection.get("scripts", []),
                        "stylesheets": dom_inspection.get("stylesheets", []),
                        "images": dom_inspection.get("images", []),
                        "iframes": dom_inspection.get("iframes", []),
                        "meta_tags": dom_inspection.get("metaTags", []),
                        "dom_info": dom_inspection.get("domInfo", {})
                    }

                except Exception as e:
                    logger.error(f"Playwright website navigation error for {url}: {str(e)}")
                    return {
                        "success": False,
                        "status_code": 0,
                        "final_url": url,
                        "page_title": "",
                        "html": "",
                        "headers": headers_captured,
                        "scripts": [],
                        "stylesheets": [],
                        "images": [],
                        "iframes": [],
                        "meta_tags": [],
                        "dom_info": {},
                        "error": str(e)
                    }

        except Exception as e:
            logger.error(f"Playwright browser launch/execution error for {url}: {str(e)}")
            return {
                "success": False,
                "status_code": 0,
                "final_url": url,
                "page_title": "",
                "html": "",
                "headers": {},
                "scripts": [],
                "stylesheets": [],
                "images": [],
                "iframes": [],
                "meta_tags": [],
                "dom_info": {},
                "error": str(e)
            }

    return await run_in_proactor_loop(_inspect)
