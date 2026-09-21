import httpx
import time
from typing import Dict, Any

async def analyze_http_response(url: str, timeout_sec: int = 15) -> Dict[str, Any]:
    """
    Performs initial HTTP GET inspection using httpx to collect status, timing,
    headers, cookies, and redirect chains.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    start_time = time.time()
    try:
        async with httpx.AsyncClient(follow_redirects=True, verify=False, timeout=timeout_sec) as client:
            response = await client.get(url, headers=headers)
            elapsed_ms = int((time.time() - start_time) * 1000)

            # Standardize headers dict
            response_headers = {k: v for k, v in response.headers.items()}
            response_cookies = {k: v for k, v in response.cookies.items()}

            return {
                "success": True,
                "status_code": response.status_code,
                "final_url": str(response.url),
                "headers": response_headers,
                "cookies": response_cookies,
                "response_time_ms": elapsed_ms,
                "history_redirects": [str(r.url) for r in response.history],
                "content_type": response.headers.get("content-type", "")
            }
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": 0,
            "final_url": url,
            "headers": {},
            "cookies": {},
            "response_time_ms": elapsed_ms,
            "error": str(e)
        }
