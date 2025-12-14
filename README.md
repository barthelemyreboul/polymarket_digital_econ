# polymarket_digital_econ
A school project for Sciences Po's Digital Economy course.

This GitHub repository contains a Python script that interacts with the Polymarket API to search for events, retrieve event metadata, extract CLOB token IDs, and download price history data for a specified token.
The objective is to observe correlations between bitcoin & political market events on Polymarket to see whether betters act similarly on it that on regular market platforms.


## Overview

This script interacts with several Polymarket API endpoints and performs a complete asynchronous workflow:

1. **Public search**
    Queries the *public-search* endpoint to retrieve events matching a given search term.

2. **Filtering events**
    Keeps 10 random events through their associated token with a transaction volume >1 000 000$ and published within a specific timeperiod.

3. **Price history download**
    Queries the *prices-history* endpoint to retrieve the price history for these tokens, using a specified interval (with a start time and an end time) or fodelity (resolution of the data) .

4. **Load into an SQLite DB**
    Eventually, load the data in a database named "polymarket.db" that will be processed on a notebook:
see: Polymarket_Digital_Economy_Project.ipynb

---

## Requirements

- python >=3.13
- see the "requirements.txt" file
- no need for credentials to access the API
---

## Run the code

1. Use Python 3.13+.
2. Install the necessary dependencies (requirements.txt):

```bash
pip install -r "requirements.txt"
```

3. Run the script to extract & load the data:

```bash
python database_init.py
```

---

