"""
data_fetcher.py

Module for collecting historical stock market data.
Supports:
1. Fetching historical price data from Yahoo Finance via yfinance.
2. Loading historical stock data from local CSV files or user uploads.
3. Validating ticker symbols and handling network/API errors gracefully.
"""

import re
from datetime import date, datetime
from typing import Union
import pandas as pd
import yfinance as yf


def validate_ticker(ticker: str) -> bool:
    """
    Validate that a stock ticker symbol has a valid format.

    Valid tickers:
    - 1 to 10 alphanumeric characters.
    - May include dot (.) or hyphen (-) for exchange suffixes (e.g. RELIANCE.NS, BRK-B).
    """
    if not ticker or not isinstance(ticker, str):
        return False
    ticker_clean = ticker.strip().upper()
    if not ticker_clean:
        return False
    # Regular expression for typical equity/index tickers
    pattern = r"^[A-Z0-9\.\-\^]{1,15}$"
    return bool(re.match(pattern, ticker_clean))


def fetch_stock_data(
    ticker: str,
    start_date: Union[str, date, datetime] = None,
    end_date: Union[str, date, datetime] = None,
) -> pd.DataFrame:
    """
    Fetch historical stock market data from Yahoo Finance using yfinance.

    Parameters:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'RELIANCE.NS').
        start_date (str | date | datetime, optional): Start date for data fetch (YYYY-MM-DD).
        end_date (str | date | datetime, optional): End date for data fetch (YYYY-MM-DD).

    Returns:
        pd.DataFrame: Raw stock data containing Date, Open, High, Low, Close, Volume.

    Raises:
        ValueError: If ticker is invalid or dates are illogical.
        RuntimeError: If data cannot be fetched or no data is returned.
    """
    ticker_clean = ticker.strip().upper()
    if not validate_ticker(ticker_clean):
        raise ValueError(
            f"Invalid ticker symbol '{ticker}'. Please enter a valid symbol (e.g. AAPL, MSFT, RELIANCE.NS)."
        )

    # Convert start and end dates to string format 'YYYY-MM-DD' if provided
    start_str = start_date.strftime("%Y-%m-%d") if isinstance(start_date, (date, datetime)) else start_date
    end_str = end_date.strftime("%Y-%m-%d") if isinstance(end_date, (date, datetime)) else end_date

    if start_str and end_str and start_str >= end_str:
        raise ValueError(f"Start date ({start_str}) must be before end date ({end_str}).")

    try:
        # Download data using yfinance
        df = yf.download(
            ticker_clean,
            start=start_str,
            end=end_str,
            auto_adjust=False,
            progress=False,
        )

        if df is None or df.empty:
            raise RuntimeError(
                f"No data found for ticker '{ticker_clean}'. "
                f"The symbol may be delisted, invalid, or the selected date range has no trading records."
            )

        # Handle yfinance multi-index columns (e.g. in yfinance >= 0.2.x)
        if isinstance(df.columns, pd.MultiIndex):
            # Flatten multi-index columns: keep primary price name
            df.columns = [col[0] for col in df.columns]

        # Reset index so that 'Date' becomes a standard column
        df = df.reset_index()

        # If 'Adj Close' is missing, fallback to 'Close'
        if "Adj Close" not in df.columns and "Close" in df.columns:
            df["Adj Close"] = df["Close"]

        return df

    except Exception as exc:
        if isinstance(exc, (ValueError, RuntimeError)):
            raise exc
        raise RuntimeError(
            f"Failed to fetch data for ticker '{ticker_clean}'. "
            f"Please check your internet connection and ticker symbol. Details: {exc}"
        ) from exc


def load_csv_data(file_or_path: Union[str, object]) -> pd.DataFrame:
    """
    Load stock data from a local CSV file path or an uploaded file-like buffer.

    Parameters:
        file_or_path: Path string to CSV, or file-like buffer (e.g., Streamlit UploadedFile).

    Returns:
        pd.DataFrame: Loaded DataFrame.

    Raises:
        ValueError: If file is empty or cannot be parsed as CSV.
    """
    try:
        df = pd.read_csv(file_or_path)
        if df.empty:
            raise ValueError("The provided CSV file contains no data.")
        return df
    except Exception as exc:
        raise ValueError(f"Failed to read CSV data: {exc}") from exc
