"""
Unit tests for data_cleaner module.
"""

import pandas as pd
import pytest
from src.data_cleaner import clean_stock_data, standardize_column_names, validate_cleaned_data


def test_standardize_column_names():
    df = pd.DataFrame({
        "date": ["2024-01-02"],
        "OPEN": [100.0],
        "high": [105.0],
        "Low": [95.0],
        "close": [102.0],
        "adj close": [102.0],
        "volume": [1000],
    })
    standardized = standardize_column_names(df)
    assert "Date" in standardized.columns
    assert "Open" in standardized.columns
    assert "High" in standardized.columns
    assert "Low" in standardized.columns
    assert "Close" in standardized.columns
    assert "Adj Close" in standardized.columns
    assert "Volume" in standardized.columns


def test_clean_stock_data_removes_duplicates_and_sorts():
    # Input has unordered dates and duplicates
    df = pd.DataFrame({
        "Date": ["2024-01-05", "2024-01-02", "2024-01-02"],
        "Open": [105.0, 100.0, 100.0],
        "High": [108.0, 103.0, 103.0],
        "Low": [104.0, 99.0, 99.0],
        "Close": [107.0, 102.0, 102.0],
        "Volume": [1500, 1000, 1000],
    })
    cleaned = clean_stock_data(df)
    assert len(cleaned) == 2
    assert pd.to_datetime(cleaned["Date"].iloc[0]) < pd.to_datetime(cleaned["Date"].iloc[1])


def test_clean_stock_data_handles_missing_values():
    df = pd.DataFrame({
        "Date": ["2024-01-02", "2024-01-03", "2024-01-04"],
        "Open": [100.0, None, 102.0],
        "High": [105.0, 106.0, None],
        "Low": [95.0, 96.0, 97.0],
        "Close": [102.0, None, 104.0],
        "Volume": [1000, None, 1200],
    })
    cleaned = clean_stock_data(df)
    assert cleaned["Close"].isna().sum() == 0
    assert cleaned["Volume"].isna().sum() == 0
    assert len(cleaned) == 3


def test_clean_stock_data_empty_raises():
    with pytest.raises(ValueError):
        clean_stock_data(pd.DataFrame())


def test_validate_cleaned_data():
    valid_df = pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-02"]),
        "Open": [100.0],
        "High": [105.0],
        "Low": [95.0],
        "Close": [102.0],
        "Volume": [1000],
    })
    is_valid, msg = validate_cleaned_data(valid_df)
    assert is_valid is True
    assert msg == "Dataset is valid."
