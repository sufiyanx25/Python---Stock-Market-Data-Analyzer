"""
data_cleaner.py

Module for cleaning, standardizing, and validating historical stock market data.
Ensures consistency across data obtained from Yahoo Finance or uploaded CSV files.
"""

from typing import Tuple
import numpy as np
import pandas as pd


# Standard column mappings to normalize various CSV/API column header formats
COLUMN_ALIASES = {
    "date": "Date",
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "adj close": "Adj Close",
    "adjclose": "Adj Close",
    "adj_close": "Adj Close",
    "adjusted close": "Adj Close",
    "volume": "Volume",
    "vol": "Volume",
}

REQUIRED_NUMERIC_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize DataFrame column names to title-case convention:
    'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'.
    """
    df = df.copy()

    # If column headers are strings with spaces/cases, map them
    rename_dict = {}
    for col in df.columns:
        col_clean = str(col).strip().lower()
        if col_clean in COLUMN_ALIASES:
            rename_dict[col] = COLUMN_ALIASES[col_clean]

    df = df.rename(columns=rename_dict)
    return df


def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw stock market DataFrame.

    Steps:
    1. Standardizes column names.
    2. Handles 'Date' formatting and ensures chronological ordering.
    3. Drops duplicate dates.
    4. Validates and converts numerical columns ('Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume').
    5. Handles missing values using forward-fill followed by backward-fill.
    6. Removes invalid rows where 'Close' price is non-positive or missing.
    7. Formats Volume as integer.

    Parameters:
        df (pd.DataFrame): Raw stock data.

    Returns:
        pd.DataFrame: Cleaned stock data.

    Raises:
        ValueError: If essential columns are missing or if DataFrame is empty after cleaning.
    """
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None.")

    df_clean = df.copy()

    # Step 1: Standardize column names
    df_clean = standardize_column_names(df_clean)

    # Check for Date column
    if "Date" not in df_clean.columns:
        # If Date is in the index
        if isinstance(df_clean.index, pd.DatetimeIndex):
            df_clean = df_clean.reset_index()
            df_clean = standardize_column_names(df_clean)
        elif "index" in [str(c).lower() for c in df_clean.columns]:
            df_clean = df_clean.rename(columns={"index": "Date"})

    if "Date" not in df_clean.columns:
        raise ValueError("Stock data must contain a 'Date' column.")

    # Step 2: Convert Date to datetime and remove time component
    df_clean["Date"] = pd.to_datetime(df_clean["Date"], errors="coerce")
    df_clean = df_clean.dropna(subset=["Date"])

    # Step 3: Remove duplicate dates and sort chronologically
    df_clean = df_clean.drop_duplicates(subset=["Date"])
    df_clean = df_clean.sort_values(by="Date", ascending=True)

    # Step 4: Validate required numeric columns
    for col in REQUIRED_NUMERIC_COLUMNS:
        if col not in df_clean.columns:
            raise ValueError(f"Required column '{col}' is missing from stock data.")

    # If 'Adj Close' is missing, fallback to 'Close'
    if "Adj Close" not in df_clean.columns:
        df_clean["Adj Close"] = df_clean["Close"]

    numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

    # Step 5: Convert numerical columns to float, coercing invalid strings to NaN
    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Step 6: Handle missing numeric values
    # Forward-fill followed by backward-fill handles isolated market holidays/missing prints
    price_cols = ["Open", "High", "Low", "Close", "Adj Close"]
    df_clean[price_cols] = df_clean[price_cols].ffill().bfill()

    # Fill any remaining volume NaNs with 0
    df_clean["Volume"] = df_clean["Volume"].fillna(0)

    # Drop any rows where 'Close' or 'Open' is still NaN or <= 0
    df_clean = df_clean.dropna(subset=["Close", "Open"])
    df_clean = df_clean[df_clean["Close"] > 0]

    if df_clean.empty:
        raise ValueError("Data cleaning resulted in an empty dataset. Check your data quality.")

    # Ensure Volume is non-negative and integer
    df_clean["Volume"] = df_clean["Volume"].clip(lower=0).astype(np.int64)

    # Standardize column order
    cols_order = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    # Include any extra columns at the end if present
    extra_cols = [c for c in df_clean.columns if c not in cols_order]
    df_clean = df_clean[cols_order + extra_cols].reset_index(drop=True)

    return df_clean


def validate_cleaned_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that cleaned DataFrame has sufficient valid data for analysis.

    Returns:
        (bool, str): (True, "OK") if valid, otherwise (False, error_message).
    """
    if df is None or df.empty:
        return False, "Dataset is empty."

    required = ["Date", "Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            return False, f"Missing required column: '{col}'."

    if len(df) < 1:
        return False, "Dataset must contain at least 1 trading day."

    return True, "Dataset is valid."
