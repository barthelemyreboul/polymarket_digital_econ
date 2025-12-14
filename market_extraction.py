import asyncio
import json
import time

from model import MarketData
from utils import get_events_by_public_search, get_trade_history_by_tokenid, clean_events, select_market




async def main_politics():
    events = await get_events_by_public_search(
        query="US Politics",
        page=100
    )
    selected_events = clean_events(events= events, number=1)
    data = []

    for event in selected_events:

        # Focus on the market with the most volume
        selected_market_index = select_market(event)
        selected_market = event["markets"][selected_market_index]

        str_token_id = selected_market["clobTokenIds"]
        asset_id = int(json.loads(str_token_id)[0])

        unix_start = 1735686000
        unix_end = 1743458400

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

            results.extend(entry for task in tasks for entry in task.get("history", []))

        data.append(MarketData(
            event_title=event["title"],
            question=selected_market["question"],
            asset_id=asset_id,
            data=results
        ))

    return data
