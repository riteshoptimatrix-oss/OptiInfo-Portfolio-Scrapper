import sys
import asyncio
import concurrent.futures
from typing import Callable, Any

async def run_in_proactor_loop(async_fn: Callable, *args: Any, **kwargs: Any) -> Any:
    """
    Executes an async function. If running on Windows and the current event loop
    is a SelectorEventLoop (or lacks subprocess support required by Playwright),
    runs the coroutine inside a dedicated ProactorEventLoop in a separate worker thread.
    """
    if sys.platform == "win32":
        try:
            loop = asyncio.get_running_loop()
            is_selector = isinstance(loop, asyncio.SelectorEventLoop) or not hasattr(loop, "_make_subprocess_transport")
        except RuntimeError:
            is_selector = False

        if is_selector:
            def _worker():
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                proactor_loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(proactor_loop)
                try:
                    return proactor_loop.run_until_complete(async_fn(*args, **kwargs))
                finally:
                    proactor_loop.close()

            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return await loop.run_in_executor(pool, _worker)

    return await async_fn(*args, **kwargs)
