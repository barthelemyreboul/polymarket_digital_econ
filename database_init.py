import sqlite3
import asyncio

from market_extraction import main_politics as market_main
from bitcoin_market import main_bitcoin
from model import MarketData


def init_db(db_path: str, table_name: str):
    """
    Initialize the database if not already present.
    Args:
        db_path (str): Path to the database
        table_name (str): Name of the table

    """
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


def insert_db(db_path: str, table_name: str, market_data : MarketData):
    """
    Inserts a new market data into the database.
    Args:
        db_path (str): Path to the database
        table_name (str): Name of the table
        market_data (MarketData): Market data object

    """
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

    # Initialize the database
    init_db(db_path="polymarket.db", table_name="market_data")

    # First get & insert bitcoin market data
    data= asyncio.run(main_bitcoin())
    db_path = "polymarket.db"
    table_name = "market_data"
    
    for market_data in data:

        insert_db(
            db_path=db_path,
            table_name= table_name,
            market_data =market_data
        )


    # Then get & insert politics market data
    data_2= asyncio.run(market_main())

    for market_data in data_2:

        insert_db(
            db_path=db_path,
            table_name= table_name,
            market_data =market_data
        )


    
