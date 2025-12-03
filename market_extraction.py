import asyncio
import json
import time
from datetime import datetime
from typing import Any, Optional

import aiohttp
import numpy as np

from utils import parse
from model import MarketData

def clean_events(events: list[dict], number: int) -> list[dict]:
    """
    Cleans the events list by removing events with low volume and returns
    a defined number of random events.
    Args:
        events (list[dict]): List of event dictionaries.
        number (int): Number of random events to return after cleaning.
    Returns:
        list[dict]: Cleaned list of event dictionaries.

    """

    for event in events:
        # Remove events with little volume
        if event.get("volume", 0) < 1000000:
            events.remove(event)
            continue
        # Remove events that started before 2020 and closed after 2024-12-12
        start = parse(event.get("startDate", "1970-01-01T00:00:00Z"))
        closed = parse(event.get("endDate", "2050-01-01T00:00:00Z"))
        if start < parse("2023-01-01T00:00:00Z") or closed > parse("2025-06-30T23:59:59Z"):
            events.remove(event)
    print(len(events), "events after cleaning")

    return list(np.random.choice(events, size=min(number, len(events)), replace=False))


async def get_events_by_public_search(
    query: str,
    event_status: Optional[str] = None,
    page: Optional[int] = 1
) -> list[dict[str, Any]]:
    """
    Perform a public search on the Polymarket API asynchronously.
    Args:
        query (str): Query string.
        event_status (str, optional): Event status. Defaults to None.
        page (int, optional): Page. Defaults to 1.
    Returns:
        list[dict[str, Any]]: List of events dictionaries.

    """

    url = "https://gamma-api.polymarket.com/public-search"
    total_events = []

    async with aiohttp.ClientSession() as session:
        for i in range(1, page + 1):
            print(f"Fetching page {i} for query '{query}'...")

            params = {
                "q": query,
                "page": i,
                "event_status":event_status,
                "sort": "volume",
                "ascending":"false"
            }

            #Clean up None values
            params = {k: v for k, v in params.items() if v is not None}

            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()

                events = data.get("events")

                if not events:
                    print(f"No events found on page {i}")
                    continue

                total_events.extend(events)

    return total_events


async def get_trade_history_by_tokenid(
        token_id: int,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
        fidelity: int = 5,
        interval: Optional[str] = None,
                        ) -> list[dict[str, Any]]:
    """
    Fetch trade history from Polymarket API based on the token ID, related to a specific market.
    Args:
        token_id (int): The CLOB token ID for which to fetch price history
        start_ts (Optionnal[int]): The start time, a Unix timestamp in UTC
        end_ts (Optionnal[int]): The end time, a Unix timestamp in UTC
        fidelity (int): The resolution of the data, in minutes
        interval (Optionnal[str]): The interval for the price history from now (e.g., '1m', '5m', '1h'). Mutually exclusive with start_ts and end_ts

    Returns:
        list[dict[str, Any]]:  List of trade history dictionaries for a given market.
    """

    url = "https://clob.polymarket.com/prices-history"

    query = {
        "market": token_id,
        "interval": interval,
        "startTs": start_ts,
        "endTs": end_ts,
        "fidelity": fidelity,
    }
    # Clean up None values
    params = {k: v for k, v in query.items() if v is not None}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

def select_market(event: dict) -> int:
    """
    Select the market index in event with the most volume from the event's markets.
    Args:
        event (dict): The event dictionary containing markets.
    Returns:
        index (int): The index of the market with the highest volume.
    """
    max_volume = -1
    index = -1
    for i, market in enumerate(event.get("markets", [])):
        volume = market.get("volume", 0)
        if float(volume) > float(max_volume):
            max_volume = volume
            index = i
    return index

async def main():
    events = await get_events_by_public_search(
        query="US Politics",
        page=100
    )
    selected_events = clean_events(events= events, number=10)
    data = []

    for event in selected_events:

        # Focus on the market with the most volume
        selected_market_index = select_market(event)
        selected_market = event["markets"][selected_market_index]

        str_token_id = selected_market["clobTokenIds"]
        asset_id = int(json.loads(str_token_id)[0])

        unix_start = int(
            datetime.fromisoformat(event["startDate"].replace(' ', 'T').replace('+00', '+00:00')).timestamp())
        unix_end = int(
            datetime.fromisoformat(event["endDate"].replace(' ', 'T').replace('+00', '+00:00')).timestamp())

        # Fetch trade history in chunks not to overload the API
        results = []
        for dl in range(unix_start, unix_end, 86400):
            time.sleep(0.1)
            tasks = []
            for hl in range(0, 86400, 28800):
                ts = dl + hl
                history= get_trade_history_by_tokenid(
                        token_id=asset_id,
                        start_ts=ts,
                        end_ts= ts+hl,
                        fidelity=5 # 5 minutes
                    )
                tasks.append(history)


            tasks = await asyncio.gather(*tasks)
            # Remove double entries in timestamp

            results.extend(entry for task in tasks for entry in task.get("history", []))

        data.append(MarketData(
            event_title=event["title"],
            question=selected_market["question"],
            asset_id=asset_id,
            data=results
        ))

    return data

