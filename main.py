import asyncio
from datetime import datetime
from typing import Optional, Any, Coroutine
import aiohttp
import requests
import json

async def get_slugs_by_public_search(
    query: str,
    page: Optional[int] = 1
) -> list[str]:
    """
    Perform a public search on the Polymarket API asynchronously.
    Returns a list of event slugs.
    """

    url = "https://gamma-api.polymarket.com/public-search"
    slugs = []

    async with aiohttp.ClientSession() as session:
        for i in range(1, page + 1):
            print(f"Fetching page {i} for query '{query}'...")

            params = {"q": query, "page": i}

            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()

                events = data.get("events")
                if not events:
                    print(f"No events found on page {i}")
                    continue

                slugs.extend(event["slug"] for event in events)

    return slugs

async def get_markets_metadata_by_slugs(
    type: str,
    slug: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    id: Optional[int] = None,
    start_date_min: Optional[datetime] = None,
) -> dict:

    allowed = ["events", "markets"]
    if type not in allowed:
        raise ValueError(f"type must be one of {allowed}")

    url = f"https://gamma-api.polymarket.com/{type}"

    query = {
        "slug": slug,
        "limit": limit,
        "offset": offset,
        "id": id,
        "start_date_min": start_date_min.isoformat() if start_date_min else None,
    }

    # Clean up None values
    params = {k: v for k, v in query.items() if v is not None}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

async def fetch_all_metadata(slugs: list[str]) -> dict[str, Any]:
    """
    Launch one coroutine per slug and gather all metadata concurrently.
    """

    # Create a coroutine for each slug
    tasks = [
        get_markets_metadata_by_slugs(type="events", slug=s)
        for s in slugs
    ]

    # Run all HTTP requests concurrently
    results = await asyncio.gather(*tasks, return_exceptions=False)


    # results is a list of metadata dicts
    return {s: r[0] for s,r in zip(slugs, results)}

async def get_trade_history_by_tokenid(
        token_id: int,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
        fidelity: int = 10,
        interval: Optional[str] = None,
                         ):
    """
    Fetch trade history from Polymarket API based on the provided slug.
    Args:
        token_id (int): The CLOB token ID for which to fetch price history
        start_ts (Optionnal[int]): The start time, a Unix timestamp in UTC
        end_ts (Optionnal[int]): The end time, a Unix timestamp in UTC
        fidelity (int): The resolution of the data, in minutes
        interval (Optionnal[str]): The interval for the price history from now (e.g., '1m', '5m', '1h'). Mutually exclusive with start_ts and end_ts

    Returns:
        dict: The JSON response containing trade history.
    """

    url = "https://clob.polymarket.com/prices-history"

    query = {
        "market": token_id,
        "interval": interval,
        "startTs": start_ts,
        "endTs": end_ts,
        "fidelity": fidelity
    }
    # Clean up None values
    params = {k: v for k, v in query.items() if v is not None}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

async def main():

    slugs = await get_slugs_by_public_search(query="bitcoin")

    metadata = await fetch_all_metadata(slugs)

    tokens_id = metadata[slugs[0]]['markets'][0]['clobTokenIds']
    yes_token = json.loads(tokens_id)[0]
    data = await get_trade_history_by_tokenid(token_id=yes_token, interval='1d', fidelity=1)
    h = data["history"]

    X = [item["t"] for item in h]
    Y = [item["p"] for item in h]

    print('ok')


if __name__ == "__main__":

    asyncio.run(main())
    print("ok")




