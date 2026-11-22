"""
report_generator.py

Module for compiling structured performance reports and exporting cleaned data.
Generates:
1. Formatted TXT analysis report.
2. Cleaned stock data CSV.
3. Disk exports inside outputs/reports/.
4. In-memory bytes for Streamlit download buttons.
"""

import os
from typing import Dict, Any, Optional
import pandas as pd


def generate_text_report(
    metrics: Dict[str, Any], df: Optional[pd.DataFrame] = None
) -> str:
    """
    Generate a formatted comprehensive text report from computed metrics and data.
    """
    t = metrics.get("ticker", "UNKNOWN")
    s_date = metrics.get("start_date", "N/A")
    e_date = metrics.get("end_date", "N/A")
    days = metrics.get("total_trading_days", 0)

    latest = metrics.get("latest_close", 0.0)
    first = metrics.get("first_close", 0.0)
    highest = metrics.get("highest_close", 0.0)
    lowest = metrics.get("lowest_close", 0.0)
    tot_ret = metrics.get("total_return_pct", 0.0)

    avg_ret = metrics.get("avg_daily_return_pct", 0.0)
    daily_vol = metrics.get("daily_volatility_pct", 0.0)
    ann_vol = metrics.get("annualized_volatility_pct", 0.0)
    avg_vol = metrics.get("avg_volume", 0.0)

    sma20 = metrics.get("latest_sma_20")
    sma50 = metrics.get("latest_sma_50")
    sma20_str = f"${sma20:,.2f}" if sma20 is not None else "N/A"
    sma50_str = f"${sma50:,.2f}" if sma50 is not None else "N/A"
    trend = metrics.get("trend_observation", "Neutral")

    divider = "=" * 68
    sub_divider = "-" * 68

    report_lines = [
        divider,
        "              STOCK MARKET DATA ANALYZER - PERFORMANCE REPORT",
        divider,
        f"Ticker Symbol          : {t}",
        f"Analyzed Date Range    : {s_date} to {e_date}",
        f"Total Trading Sessions : {days} days",
        "",
        "1. PRICE & RETURN PERFORMANCE",
        sub_divider,
        f"Starting Close Price   : ${first:,.2f}",
        f"Latest Close Price     : ${latest:,.2f}",
        f"Period Peak Price      : ${highest:,.2f}",
        f"Period Trough Price    : ${lowest:,.2f}",
        f"Total Period Return    : {tot_ret:+.2f}%",
        "",
        "2. RISK & VOLATILITY PROFILE",
        sub_divider,
        f"Average Daily Return   : {avg_ret:+.2f}%",
        f"Daily Volatility (Std) : {daily_vol:.2f}%",
        f"Annualized Volatility  : {ann_vol:.2f}% (based on 252 trading days)",
        f"Average Daily Volume   : {avg_vol:,.0f} shares",
        "",
        "3. TECHNICAL INDICATORS",
        sub_divider,
        f"20-Day SMA (Latest)    : {sma20_str}",
        f"50-Day SMA (Latest)    : {sma50_str}",
        f"Trend Classification   : {trend}",
        "",
        "4. ANALYTICAL SUMMARY",
        sub_divider,
        f"During the analyzed period ({s_date} to {e_date}), {t} recorded a cumulative",
        f"return of {tot_ret:+.2f}%, fluctuating between a minimum of ${lowest:,.2f} and a",
        f"maximum of ${highest:,.2f}. The daily price movements exhibited an annualized",
        f"volatility of {ann_vol:.2f}%, indicating the degree of market dispersion.",
        f"The technical posture is currently classified as '{trend}'.",
        "",
        divider,
        "DISCLAIMER:",
        "This project is intended for educational and analytical purposes only. It does not provide financial advice or investment recommendations.",
        divider,
    ]

    return "\n".join(report_lines)


def save_text_report(
    report_content: str, ticker: str, output_dir: str = "outputs/reports"
) -> str:
    """
    Save report string to a text file inside outputs/reports/.

    Returns:
        str: Absolute path of saved report file.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{ticker.upper()}_analysis_report.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)

    return os.path.abspath(filepath)


def export_cleaned_csv(
    df: pd.DataFrame, ticker: str, output_dir: str = "outputs/reports"
) -> str:
    """
    Save cleaned stock data to CSV file inside outputs/reports/.

    Returns:
        str: Absolute path of saved CSV file.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{ticker.upper()}_cleaned_data.csv"
    filepath = os.path.join(output_dir, filename)

    df.to_csv(filepath, index=False)
    return os.path.abspath(filepath)


def generate_csv_download(df: pd.DataFrame) -> bytes:
    """
    Encode DataFrame into CSV bytes for Streamlit st.download_button.
    """
    return df.to_csv(index=False).encode("utf-8")


def generate_txt_download(report_content: str) -> bytes:
    """
    Encode text report into bytes for Streamlit st.download_button.
    """
    return report_content.encode("utf-8")
