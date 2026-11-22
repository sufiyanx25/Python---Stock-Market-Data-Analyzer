"""
database.py

Module for persisting and querying historical stock market data using SQLite.
Stores:
- ticker
- date
- open
- high
- low
- close
- adj_close
- volume

Prevents duplicate records using a UNIQUE(ticker, date) constraint.
"""

import os
import sqlite3
from typing import List, Optional
import pandas as pd


DEFAULT_DB_PATH = "data/stock_database.db"


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Create a database connection and ensure parent directories exist.
    """
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initialize SQLite database schema for stock market data.
    Creates table 'stocks' with UNIQUE constraint on (ticker, date) to prevent duplicates.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL,
            volume INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, date)
        )
        """
    )

    # Index for fast queries by ticker and date
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_stocks_ticker_date ON stocks(ticker, date)"
    )

    conn.commit()
    conn.close()


def save_stock_data(
    df: pd.DataFrame, ticker: str, db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Insert or update stock market records into the SQLite database.
    Avoids duplicate entries by using 'INSERT OR REPLACE'.

    Parameters:
        df (pd.DataFrame): Cleaned stock data with Date, Open, High, Low, Close, Adj Close, Volume.
        ticker (str): Ticker symbol.
        db_path (str): Path to SQLite database file.

    Returns:
        int: Number of records successfully inserted or replaced.
    """
    if df is None or df.empty:
        return 0

    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    ticker_clean = ticker.strip().upper()
    records_to_insert = []

    for _, row in df.iterrows():
        # Format date as 'YYYY-MM-DD'
        date_val = str(pd.to_datetime(row["Date"]).strftime("%Y-%m-%d"))
        open_val = float(row["Open"]) if pd.notnull(row["Open"]) else None
        high_val = float(row["High"]) if pd.notnull(row["High"]) else None
        low_val = float(row["Low"]) if pd.notnull(row["Low"]) else None
        close_val = float(row["Close"]) if pd.notnull(row["Close"]) else None
        adj_close_val = (
            float(row["Adj Close"])
            if "Adj Close" in row and pd.notnull(row["Adj Close"])
            else close_val
        )
        volume_val = int(row["Volume"]) if pd.notnull(row["Volume"]) else 0

        records_to_insert.append(
            (
                ticker_clean,
                date_val,
                open_val,
                high_val,
                low_val,
                close_val,
                adj_close_val,
                volume_val,
            )
        )

    # Use INSERT OR REPLACE to update existing dates without duplicating
    query = """
        INSERT OR REPLACE INTO stocks (
            ticker, date, open, high, low, close, adj_close, volume
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(query, records_to_insert)
    inserted_count = len(records_to_insert)

    conn.commit()
    conn.close()
    return inserted_count


def load_stock_from_db(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """
    Load stock records from the SQLite database for a given ticker and date range.

    Parameters:
        ticker (str): Stock ticker symbol.
        start_date (str, optional): Start date (YYYY-MM-DD).
        end_date (str, optional): End date (YYYY-MM-DD).
        db_path (str): Path to SQLite database file.

    Returns:
        pd.DataFrame: DataFrame containing retrieved stock records.
    """
    if not os.path.exists(db_path):
        return pd.DataFrame()

    conn = get_connection(db_path)
    ticker_clean = ticker.strip().upper()

    query = "SELECT date, open, high, low, close, adj_close, volume FROM stocks WHERE ticker = ?"
    params = [ticker_clean]

    if start_date:
        query += " AND date >= ?"
        params.append(str(start_date))

    if end_date:
        query += " AND date <= ?"
        params.append(str(end_date))

    query += " ORDER BY date ASC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if not df.empty:
        # Standardize column naming convention
        df = df.rename(
            columns={
                "date": "Date",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "adj_close": "Adj Close",
                "volume": "Volume",
            }
        )
        df["Date"] = pd.to_datetime(df["Date"])

    return df


def get_available_tickers(db_path: str = DEFAULT_DB_PATH) -> List[str]:
    """
    Get list of unique tickers stored in the SQLite database.
    """
    if not os.path.exists(db_path):
        return []

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT ticker FROM stocks ORDER BY ticker ASC")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def get_records_count(
    ticker: Optional[str] = None, db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Return total count of records in the database, optionally filtered by ticker.
    """
    if not os.path.exists(db_path):
        return 0

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        if ticker:
            cursor.execute(
                "SELECT COUNT(*) FROM stocks WHERE ticker = ?", (ticker.strip().upper(),)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM stocks")
        count = cursor.fetchone()[0]
        return count
    except sqlite3.OperationalError:
        return 0
    finally:
        conn.close()
