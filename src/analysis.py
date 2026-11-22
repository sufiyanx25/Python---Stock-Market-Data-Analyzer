"""
analysis.py

Module for quantitative and technical analysis of stock market data.
Calculates:
- Daily percentage returns
- 20-day Simple Moving Average (SMA 20)
- 50-day Simple Moving Average (SMA 50)
- Average daily return
- Annualized volatility (assuming 252 trading days)
- Highest and lowest closing prices
- Average trading volume
- Comprehensive summary statistics and text summary
"""

from typing import Dict, Any
import numpy as np
import pandas as pd


def calculate_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily percentage returns based on the 'Close' price.

    Formula:
        Daily_Return_t = ((Close_t - Close_{t-1}) / Close_{t-1}) * 100

    Returns:
        pd.DataFrame: DataFrame with added 'Daily_Return' column.
    """
    df = df.copy()
    if "Close" not in df.columns:
        raise ValueError("DataFrame must contain 'Close' column to calculate returns.")

    # Calculate percentage change in close price
    df["Daily_Return"] = df["Close"].pct_change() * 100.0
    return df


def calculate_moving_averages(
    df: pd.DataFrame, window_short: int = 20, window_long: int = 50
) -> pd.DataFrame:
    """
    Calculate short-term (e.g., 20-day) and long-term (e.g., 50-day) Simple Moving Averages.

    Formula:
        SMA_N = sum(Close_{t-i} for i in range(N)) / N

    Parameters:
        df (pd.DataFrame): Stock data with 'Close' column.
        window_short (int): Window length for short-term moving average (default: 20).
        window_long (int): Window length for long-term moving average (default: 50).

    Returns:
        pd.DataFrame: DataFrame with 'SMA_20' and 'SMA_50' columns added.
    """
    df = df.copy()
    if "Close" not in df.columns:
        raise ValueError("DataFrame must contain 'Close' column to calculate moving averages.")

    col_short = f"SMA_{window_short}"
    col_long = f"SMA_{window_long}"

    df[col_short] = df["Close"].rolling(window=window_short, min_periods=1).mean()
    df[col_long] = df["Close"].rolling(window=window_long, min_periods=1).mean()

    return df


def compute_summary_metrics(df: pd.DataFrame, ticker: str = "STOCK") -> Dict[str, Any]:
    """
    Compute key performance, risk, and volume metrics for the analyzed period.

    Metrics calculated:
    - Selected ticker
    - Date range analyzed (start and end date)
    - Total trading days
    - Latest available closing price
    - Highest closing price
    - Lowest closing price
    - Average daily return (%)
    - Daily return standard deviation (%)
    - Annualized volatility (%) [std_daily * sqrt(252)]
    - Average trading volume
    - Total return over the period (%)
    - Latest SMA 20 & SMA 50 values (if available)

    Parameters:
        df (pd.DataFrame): Cleaned stock data with or without returns/SMA columns.
        ticker (str): Ticker symbol.

    Returns:
        dict: Dictionary of computed numerical and string metrics.
    """
    if df is None or df.empty:
        raise ValueError("Cannot compute metrics on an empty dataset.")

    # Ensure returns and SMAs are calculated
    analysis_df = df.copy()
    if "Daily_Return" not in analysis_df.columns:
        analysis_df = calculate_daily_returns(analysis_df)
    if "SMA_20" not in analysis_df.columns or "SMA_50" not in analysis_df.columns:
        analysis_df = calculate_moving_averages(analysis_df, 20, 50)

    # Date formatting
    dates = pd.to_datetime(analysis_df["Date"])
    start_date = dates.min().strftime("%Y-%m-%d")
    end_date = dates.max().strftime("%Y-%m-%d")
    total_days = len(analysis_df)

    # Price metrics
    close_series = analysis_df["Close"]
    latest_close = float(close_series.iloc[-1])
    first_close = float(close_series.iloc[0])
    highest_close = float(close_series.max())
    lowest_close = float(close_series.min())

    # Period total return
    total_return = ((latest_close - first_close) / first_close) * 100.0 if first_close > 0 else 0.0

    # Daily Return & Volatility metrics
    returns_clean = analysis_df["Daily_Return"].dropna()
    if len(returns_clean) > 0:
        avg_daily_return = float(returns_clean.mean())
        daily_volatility = float(returns_clean.std()) if len(returns_clean) > 1 else 0.0
        # Annualized Volatility formula: Daily Return StdDev * sqrt(252)
        annualized_volatility = float(daily_volatility * np.sqrt(252))
    else:
        avg_daily_return = 0.0
        daily_volatility = 0.0
        annualized_volatility = 0.0

    # Volume metrics
    avg_volume = float(analysis_df["Volume"].mean()) if "Volume" in analysis_df.columns else 0.0

    # Moving average latest values
    latest_sma_20 = float(analysis_df["SMA_20"].iloc[-1]) if "SMA_20" in analysis_df.columns else None
    latest_sma_50 = float(analysis_df["SMA_50"].iloc[-1]) if "SMA_50" in analysis_df.columns else None

    # Trend observation
    trend = "Neutral"
    if latest_sma_20 and latest_sma_50:
        if latest_close >= latest_sma_20 and latest_sma_20 >= latest_sma_50:
            trend = "Bullish (Price above SMA 20 and SMA 50)"
        elif latest_close < latest_sma_20 and latest_sma_20 < latest_sma_50:
            trend = "Bearish (Price below SMA 20 and SMA 50)"
        elif latest_close >= latest_sma_20:
            trend = "Moderately Bullish (Price above SMA 20)"
        else:
            trend = "Moderately Bearish (Price below SMA 20)"

    return {
        "ticker": ticker.upper(),
        "start_date": start_date,
        "end_date": end_date,
        "total_trading_days": total_days,
        "latest_close": latest_close,
        "first_close": first_close,
        "highest_close": highest_close,
        "lowest_close": lowest_close,
        "total_return_pct": total_return,
        "avg_daily_return_pct": avg_daily_return,
        "daily_volatility_pct": daily_volatility,
        "annualized_volatility_pct": annualized_volatility,
        "avg_volume": avg_volume,
        "latest_sma_20": latest_sma_20,
        "latest_sma_50": latest_sma_50,
        "trend_observation": trend,
    }


def generate_text_summary(metrics: Dict[str, Any]) -> str:
    """
    Generate a factual, text-based analytical summary from computed metrics.
    No fabricated data. Suitable for educational display and downloadable reports.
    """
    t = metrics["ticker"]
    s_date = metrics["start_date"]
    e_date = metrics["end_date"]
    days = metrics["total_trading_days"]
    latest = metrics["latest_close"]
    highest = metrics["highest_close"]
    lowest = metrics["lowest_close"]
    tot_ret = metrics["total_return_pct"]
    avg_ret = metrics["avg_daily_return_pct"]
    ann_vol = metrics["annualized_volatility_pct"]
    avg_vol = metrics["avg_volume"]
    trend = metrics["trend_observation"]

    sma20_str = f"${metrics['latest_sma_20']:.2f}" if metrics.get("latest_sma_20") else "N/A"
    sma50_str = f"${metrics['latest_sma_50']:.2f}" if metrics.get("latest_sma_50") else "N/A"

    lines = [
        f"STOCK PERFORMANCE SUMMARY: {t}",
        "=" * 50,
        f"Analyzed Period      : {s_date} to {e_date} ({days} trading days)",
        f"Latest Closing Price : ${latest:,.2f}",
        f"Highest Close        : ${highest:,.2f}",
        f"Lowest Close         : ${lowest:,.2f}",
        f"Overall Period Return: {tot_ret:+.2f}%",
        f"Average Daily Return : {avg_ret:+.2f}%",
        f"Annualized Volatility: {ann_vol:.2f}%",
        f"Average Daily Volume : {avg_vol:,.0f} shares",
        f"20-Day SMA (Latest)  : {sma20_str}",
        f"50-Day SMA (Latest)  : {sma50_str}",
        f"Technical Posture    : {trend}",
        "",
        "ANALYSIS COMMENTARY:",
        f"Over the {days} trading days between {s_date} and {e_date}, {t} traded between a low",
        f"of ${lowest:,.2f} and a high of ${highest:,.2f}, closing most recently at ${latest:,.2f}.",
        f"The stock experienced an average daily return of {avg_ret:+.2f}%, leading to an annualized",
        f"volatility of {ann_vol:.2f}%. Trading activity averaged {avg_vol:,.0f} shares traded daily.",
        f"From a technical moving average standpoint, the latest price position relative to the",
        f"20-day SMA ({sma20_str}) and 50-day SMA ({sma50_str}) indicates a {trend} posture.",
        "",
        "DISCLAIMER:",
        "This project is intended for educational and analytical purposes only. It does not provide financial advice or investment recommendations.",
    ]
    return "\n".join(lines)
