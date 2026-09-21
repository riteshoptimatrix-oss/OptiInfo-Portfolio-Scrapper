import sys
import asyncio
from playwright.async_api import async_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def main():
    print("Starting Playwright...", flush=True)
    async with async_playwright() as p:
        print("Launching Chromium...", flush=True)
        browser = await p.chromium.launch(headless=True)
        try:
            print("Opening website...", flush=True)
            context = await browser.new_context()
            page = await context.new_page()
            response = await page.goto("https://www.optiinfo.com/our-works/", wait_until="domcontentloaded", timeout=45000)
            if response and response.ok:
                print("Page loaded successfully", flush=True)
            else:
                print(f"Page loaded with status: {response.status if response else 'No response'}", flush=True)
            title = await page.title()
            print(f"Title: {title}", flush=True)
            print(f"URL: {page.url}", flush=True)
            await context.close()
        finally:
            await browser.close()
    print("Playwright test successful!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
