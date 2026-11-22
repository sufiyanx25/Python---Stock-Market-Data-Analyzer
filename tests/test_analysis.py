"""
Unit tests for analysis module.
"""

import numpy as np
import pandas as pd
import pytest
from src.analysis import (
    calculate_daily_returns,
    calculate_moving_averages,
    compute_summary_metrics,
    generate_text_summary,
)


@pytest.fixture
def sample_stock_df():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    prices = [100.0, 102.0, 101.0, 105.0, 107.0, 106.0, 110.0, 109.0, 112.0, 115.0]
    return pd.DataFrame({
        "Date": dates,
        "Open": prices,
        "High": [p + 2 for p in prices],
        "Low": [p - 2 for p in prices],
        "Close": prices,
        "Adj Close": prices,
        "Volume": [100000] * 10,
    })


def test_calculate_daily_returns(sample_stock_df):
    df_ret = calculate_daily_returns(sample_stock_df)
    assert "Daily_Return" in df_ret.columns
    assert pd.isna(df_ret["Daily_Return"].iloc[0])
    # Second day: (102 - 100) / 100 * 100 = 2.0%
    assert pytest.approx(df_ret["Daily_Return"].iloc[1], 0.01) == 2.0


def test_calculate_moving_averages(sample_stock_df):
    df_ma = calculate_moving_averages(sample_stock_df, 3, 5)
    assert "SMA_3" in df_ma.columns
    assert "SMA_5" in df_ma.columns
    # 3-day MA at index 2: (100 + 102 + 101) / 3 = 101.0
    assert pytest.approx(df_ma["SMA_3"].iloc[2], 0.01) == 101.0


def test_compute_summary_metrics(sample_stock_df):
    metrics = compute_summary_metrics(sample_stock_df, ticker="TEST")
    assert metrics["ticker"] == "TEST"
    assert metrics["highest_close"] == 115.0
    assert metrics["lowest_close"] == 100.0
    assert metrics["total_trading_days"] == 10
    assert metrics["annualized_volatility_pct"] > 0
    assert metrics["avg_volume"] == 100000.0


def test_generate_text_summary(sample_stock_df):
    metrics = compute_summary_metrics(sample_stock_df, ticker="TEST")
    summary = generate_text_summary(metrics)
    assert "TEST" in summary
    assert "Latest Closing Price" in summary
    assert "DISCLAIMER" in summary
