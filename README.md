# polymarket_digital_econ
A school project for Sciences Po's Digital Economy course.

This GitHub repository contains a Python script that interacts with the Polymarket API to search for events, retrieve event metadata, extract CLOB token IDs, and download price history data for a specified token.
The objective is to observe correlations between bitcoin & political market events on Polymarket to see whether betters act similarly on it that on regular market platforms.


## Overview

This script interacts with several Polymarket API endpoints and performs a complete asynchronous workflow:

1. **Public search**
   Queries the *public-search* endpoint to retrieve events matching a given search term.

2. **Filtering events**
   Keeps 10 random events with a transaction volume >1 000 000$ and published within a specific timeperiod.

3**Price history download**
   It queries the *prices-history* endpoint to retrieve the price history for that token, using a specified interval (here `1d`) and fidelity (`1`).


---

## Requirements

*(You will fill this section.)*

---

## Run the code

1. Use Python 3.10+.
2. Install the necessary dependencies:

```bash
pip install aiohttp requests matplotlib
```

3. Run the script:

```bash
python market_extraction.py
```
To extract the data, and:

```bash
python database.py
```
to store it in a local SQLite database.

The script will:

* search for `"bitcoin"`,
* fetch metadata for all matching events,
* extract a CLOB token ID,
* retrieve its price history,
* extract timestamps and prices,
* print `"ok"` at completion.

---

## References

*(You will fill this section.)*

---
