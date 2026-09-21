import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.logging import setup_logging
from app.scraper.portfolio_scraper import OptiInfoPortfolioScraper

logger = setup_logging()

async def main():
    parser = argparse.ArgumentParser(description="OptiInfo Portfolio Playwright Scraper CLI")
    parser.add_argument("--headful", action="store_true", help="Run browser in headful (visible) mode")
    parser.add_argument("--timeout", type=int, default=45000, help="Navigation timeout in milliseconds")
    parser.add_argument("--output", type=str, default="scratch/extracted_portfolio.json", help="Path to save extracted JSON result")
    args = parser.parse_args()

    headless = not args.headful
    logger.info(f"Starting Scraper CLI (Headless: {headless}, Timeout: {args.timeout}ms)")

    scraper = OptiInfoPortfolioScraper(headless=headless, timeout_ms=args.timeout)
    result = await scraper.scrape()

    print("\n" + "=" * 60)
    print("SCRAPER RESULTS SUMMARY")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Total Found: {result['total_found']}")
    print(f"Successful Extracted: {result['successful']}")
    print(f"Failed Records: {result['failed']}")
    print("=" * 60)

    if result.get("records"):
        print("\nFIRST 5 EXTRACTED RECORDS:")
        print(json.dumps(result["records"][:5], indent=2))

        # Save to output path if specified
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved full results ({len(result['records'])} records) to {output_path}")

    if not result["success"]:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
