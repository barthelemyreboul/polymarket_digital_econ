import asyncio
import time

from model import MarketData
from market_extraction import get_trade_history_by_tokenid


async def main_bitcoin():

    data = []

    unix_start = 1735686000
    unix_end = 	1743458400

    # Fetch trade history in chunks not to overload the API
    results = []
    for dl in range(unix_start, unix_end, 86400):
        time.sleep(0.1)
        tasks = []
        for hl in range(0, 86400, 28800):
            ts = dl + hl
            history = get_trade_history_by_tokenid(
                token_id=95047670164958340277111777643825971965059782358468932324606496632183052684085,
                start_ts=ts,
                end_ts=ts + hl,
                fidelity=5,  # 5 minutes
            )
            tasks.append(history)


        tasks = await asyncio.gather(*tasks)
        # Remove double entries in timestamp

        results.extend(entry for task in tasks for entry in task.get("history", []))

    data.append(MarketData(
        event_title="What price will Bitcoin hit in 2025?",
        question="Will Bitcoin reach $70,000 by December 31, 2025?",
        asset_id=95047670164958340277111777643825971965059782358468932324606496632183052684085,
        data=results
    ))

    return data

if __name__ == "__main__":

    asyncio.run(main_bitcoin())