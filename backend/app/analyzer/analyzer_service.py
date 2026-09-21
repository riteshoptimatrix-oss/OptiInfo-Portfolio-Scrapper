import logging
from typing import Dict, Any
from app.analyzer.security import is_safe_url
from app.analyzer.http_analyzer import analyze_http_response
from app.analyzer.browser_analyzer import analyze_website_with_playwright
from app.analyzer.dns_analyzer import analyze_dns_records
from app.analyzer.ssl_analyzer import analyze_ssl_certificate
from app.analyzer.fingerprint_engine import fingerprint_engine

logger = logging.getLogger("optiinfo_scraper.analyzer_service")

class WebsiteAnalyzerPipeline:
    """
    Website Analysis Engine Coordinator & Pipeline Execution.
    Validates URL safety, executes HTTP/Playwright/DNS/SSL analyzers,
    and runs the fingerprint engine to produce evidence-backed tech detection.
    """
    async def analyze_website(self, target_url: str) -> Dict[str, Any]:
        logger.info(f"Initiating full website analysis pipeline for: {target_url}")

        # 1. SSRF URL Security Validation
        is_safe, error_reason = is_safe_url(target_url)
        if not is_safe:
            logger.warning(f"SSRF URL Validation blocked target {target_url}: {error_reason}")
            return {
                "success": False,
                "error": f"SSRF Security Violation: {error_reason}"
            }

        try:
            # 2. HTTP Response Inspection
            logger.info(f"Step 1/4: HTTP response & header analysis for {target_url}...")
            http_data = await analyze_http_response(target_url)

            # 3. Playwright DOM & Resource Inspection
            logger.info(f"Step 2/4: Playwright Chromium DOM & asset inspection for {target_url}...")
            browser_data = await analyze_website_with_playwright(target_url)

            # 4. DNS Resolution
            logger.info(f"Step 3/4: DNS record analysis for {target_url}...")
            dns_data = analyze_dns_records(target_url)

            # 5. SSL/TLS Inspection
            logger.info(f"Step 4/4: SSL/TLS certificate inspection for {target_url}...")
            ssl_data = analyze_ssl_certificate(target_url)

            # Check if at least one inspection method yielded results
            if not http_data.get("success") and not browser_data.get("success"):
                error_msg = browser_data.get("error") or http_data.get("error") or "Website unreachable or timed out."
                logger.warning(f"Both HTTP and Playwright failed for {target_url}: {error_msg}")
                return {
                    "success": False,
                    "error": f"Website analysis failed: {error_msg}"
                }

            # 6. Run Central Fingerprint Engine
            logger.info(f"Synthesizing technology fingerprints & evidence for {target_url}...")
            result = fingerprint_engine.run_fingerprint_analysis(
                target_url=target_url,
                browser_data=browser_data,
                http_data=http_data,
                dns_data=dns_data,
                ssl_data=ssl_data
            )

            result["success"] = True
            return result

        except Exception as e:
            logger.error(f"Unhandled exception during website analysis for {target_url}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Analysis pipeline error: {str(e)}"
            }

analyzer_pipeline = WebsiteAnalyzerPipeline()
