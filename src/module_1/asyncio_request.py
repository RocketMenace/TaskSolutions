import asyncio
import json

import aiohttp


async def fetch_urls(urls: list[str], file_path: str) -> dict[str, int]:
    semaphore = asyncio.Semaphore(5)
    results: dict[str, int] = dict()

    async with aiohttp.ClientSession() as session:
        async def make_request(url: str):
            async with semaphore:
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        return url, response.status
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    return url, 0

        url_status_pairs = await asyncio.gather(*[make_request(url) for url in urls])

    results = dict(url_status_pairs)

    with open(file_path, "w", encoding="utf-8") as f:
        for url, status_code in url_status_pairs:
            json_line = json.dumps({"url": url, "status_code": status_code}, ensure_ascii=False) + "\n"
            f.write(json_line)

    return results


if __name__ == "__main__":
    urls_list = [
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url",
    ]

    asyncio.run(fetch_urls(urls_list, "./results.json"))
