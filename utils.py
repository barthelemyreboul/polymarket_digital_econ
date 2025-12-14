from datetime import datetime, timezone
from typing import Any, Optional
import aiohttp
import numpy as np

def parse_iso_z(ts: str) -> datetime:
    """
    Parse an ISO 8601 timestamp with 'Z' suffix to a datetime object in UTC.
    Args:
        ts (str): ISO 8601 timestamp string.
    Returns:
        datetime: A timezone-aware datetime object in UTC.
    """

    ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def clean_events(events: list[dict], number: int) -> list[dict[str, Any]]:
    """
    Clean and filter events based on volume and date range.
    Args:
        events (list[dict]): List of event dictionaries.
        number (int): Number of events to select randomly after filtering.
    Returns:
        list[dict[str, Any]]: Filtered list of event dictionaries.
    """

    min_start = parse_iso_z("2024-09-01T00:00:00Z")
    max_start = parse_iso_z("2025-02-01T00:00:00Z")

    filtered = []

    for event in events:

        # Filtering on volume
        volume = event.get("volume", 0)
        if volume < 1000000:
            continue

        # Filtering on date range
        start = parse_iso_z(event.get("startDate", "1970-01-01T00:00:00Z"))
        closed = parse_iso_z(event.get("closedTime", "2050-01-01T00:00:00Z"))

        if (start >= min_start and start <= max_start):
            filtered.append(event)

    print(len(filtered), "events after cleaning")

    # Sélection aléatoire
    return list(np.random.choice(filtered,
                                 size=min(number, len(filtered)),
                                 replace=False))


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
                "event_status": event_status,
                "sort": "volume",
                "ascending": "false"
            }

            # Clean up None values
            params = {k: v for k, v in params.items() if v is not None}

            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()

                events = data.get("events")

                if not events:
                    print(f"No events found on page {i}")
                    continue

                total_events.extend(events)
    print(f"Total events fetched: {len(total_events)}")
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