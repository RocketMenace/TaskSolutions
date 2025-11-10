import asyncio
import json
from pathlib import Path

import aiohttp


async def fetch_single_url(
    url: str,
    semaphore: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    timeout: aiohttp.ClientTimeout,
) -> dict | None:
    async with semaphore:
        try:
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                content = await response.json()
                return {"url": url, "content": content}
        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            json.JSONDecodeError,
            aiohttp.ClientResponseError,
        ):
            return None


async def fetch_urls(
    input_file: str | Path,
    output_file: str | Path = "result.json",
    max_concurrent: int = 5,
    timeout_seconds: int = 300,
) -> None:
    input_path = Path(input_file)
    output_path = Path(output_file)

    with open(input_path, "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file if line.strip()]

    if not urls:
        return

    semaphore = asyncio.Semaphore(max_concurrent)

    timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    with open(output_path, "w", encoding="utf-8") as output_f:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_single_url(url, semaphore, session, timeout) for url in urls]

            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result is not None:
                    json_line = json.dumps(result, ensure_ascii=False) + "\n"
                    output_f.write(json_line)
                    output_f.flush()


if __name__ == "__main__":
    asyncio.run(fetch_urls("urls.txt", "result.json"))
