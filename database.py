import sqlite3
import asyncio

from market_extraction import main as market_main
from model import MarketData


def init_db(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_title TEXT,
            question TEXT,
            price REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_db(db_path, table_name, market_data : MarketData):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for entry in market_data.data:
        cursor.execute(
            f"""
            INSERT INTO {table_name} (event_title, question, price, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                market_data.event_title,
                market_data.question,
                entry["p"],
                str(entry["t"]),
            ),
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db(db_path="polymarket.db", table_name="market_data")
    
    data= asyncio.run(market_main())
    db_path = "polymarket.db"
    table_name = "market_data"
    
    for market_data in data:
    
        insert_db(
            db_path=db_path,
            table_name= table_name,
            market_data =market_data
        )
    
