"""
visualization.py

Module for creating professional stock market visual charts using Matplotlib and Seaborn.
Generates:
1. Historical Closing Price Chart
2. Closing Price with SMA 20 and SMA 50 Overlays
3. Daily Returns Chart (with zero baseline and green/red highlights)
4. Daily Return Distribution Chart (Histogram with KDE)
5. Trading Volume Chart
"""

import os
from typing import Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd


# Set clean seaborn aesthetic style
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams["figure.autolayout"] = True
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11


def plot_closing_price(
    df: pd.DataFrame, ticker: str = "STOCK", save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate a historical closing price line chart.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    dates = pd.to_datetime(df["Date"])

    ax.plot(dates, df["Close"], color="#1f77b4", linewidth=2.0, label="Close Price")
    ax.fill_between(dates, df["Close"], color="#1f77b4", alpha=0.1)

    ax.set_title(f"{ticker} - Historical Closing Price", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD / Local Currency)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=30)
    ax.legend(loc="upper left")

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_moving_averages(
    df: pd.DataFrame, ticker: str = "STOCK", save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate closing price line chart with 20-day and 50-day SMA overlays.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    dates = pd.to_datetime(df["Date"])

    ax.plot(dates, df["Close"], color="#2c3e50", linewidth=1.8, label="Close Price", alpha=0.85)

    if "SMA_20" in df.columns:
        ax.plot(dates, df["SMA_20"], color="#27ae60", linewidth=1.8, label="20-Day SMA", linestyle="--")

    if "SMA_50" in df.columns:
        ax.plot(dates, df["SMA_50"], color="#e67e22", linewidth=1.8, label="50-Day SMA", linestyle="-.")

    ax.set_title(f"{ticker} - Price Trend with Moving Averages (SMA 20 & SMA 50)", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=30)
    ax.legend(loc="best")

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_daily_returns(
    df: pd.DataFrame, ticker: str = "STOCK", save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate daily percentage returns chart over time with a zero baseline.
    """
    fig, ax = plt.subplots(figsize=(10, 4.5))
    dates = pd.to_datetime(df["Date"])
    returns = df["Daily_Return"] if "Daily_Return" in df.columns else df["Close"].pct_change() * 100

    colors = ["#2ecc71" if r >= 0 else "#e74c3c" for r in returns.fillna(0)]
    ax.bar(dates, returns, color=colors, width=1.5, alpha=0.75, label="Daily Return (%)")
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8)

    ax.set_title(f"{ticker} - Daily Percentage Returns", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Return (%)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=30)

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_return_distribution(
    df: pd.DataFrame, ticker: str = "STOCK", save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate daily return distribution histogram with Kernel Density Estimation (KDE).
    """
    fig, ax = plt.subplots(figsize=(10, 4.5))
    returns = (df["Daily_Return"] if "Daily_Return" in df.columns else df["Close"].pct_change() * 100).dropna()

    if len(returns) > 1:
        sns.histplot(returns, kde=True, color="#3498db", bins=30, ax=ax, stat="density", alpha=0.6)
        mean_ret = returns.mean()
        std_ret = returns.std()
        ax.axvline(mean_ret, color="#e74c3c", linestyle="--", linewidth=1.5, label=f"Mean: {mean_ret:+.2f}%")
        ax.axvline(mean_ret + std_ret, color="#95a5a6", linestyle=":", linewidth=1.2, label=f"+1 Std: {mean_ret + std_ret:.2f}%")
        ax.axvline(mean_ret - std_ret, color="#95a5a6", linestyle=":", linewidth=1.2, label=f"-1 Std: {mean_ret - std_ret:.2f}%")
        ax.legend(loc="upper right")
    else:
        ax.text(0.5, 0.5, "Insufficient data points for return distribution", ha="center", va="center")

    ax.set_title(f"{ticker} - Daily Return Distribution & Volatility", pad=12)
    ax.set_xlabel("Daily Return (%)")
    ax.set_ylabel("Density")

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_volume(
    df: pd.DataFrame, ticker: str = "STOCK", save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate trading volume bar chart over time with a 20-day rolling average line.
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    dates = pd.to_datetime(df["Date"])
    volume = df["Volume"]

    ax.bar(dates, volume, color="#9b59b6", alpha=0.6, width=1.5, label="Trading Volume")

    # Rolling average volume
    if len(volume) >= 5:
        vol_sma = volume.rolling(window=min(20, len(volume)), min_periods=1).mean()
        ax.plot(dates, vol_sma, color="#8e44ad", linewidth=1.8, label="20-Day Avg Volume")

    ax.set_title(f"{ticker} - Trading Volume History", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume (Shares)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=30)
    ax.legend(loc="upper left")

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def save_all_charts(
    df: pd.DataFrame, ticker: str = "STOCK", output_dir: str = "outputs/charts"
) -> Dict[str, str]:
    """
    Generate and save all 5 required charts to the outputs/charts/ directory.

    Returns:
        dict: Mapping of chart name to saved file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    t = ticker.upper()

    charts = {
        "closing_price": os.path.join(output_dir, f"{t}_closing_price.png"),
        "moving_averages": os.path.join(output_dir, f"{t}_moving_averages.png"),
        "daily_returns": os.path.join(output_dir, f"{t}_daily_returns.png"),
        "return_distribution": os.path.join(output_dir, f"{t}_return_distribution.png"),
        "trading_volume": os.path.join(output_dir, f"{t}_trading_volume.png"),
    }

    fig1 = plot_closing_price(df, t, save_path=charts["closing_price"])
    plt.close(fig1)

    fig2 = plot_moving_averages(df, t, save_path=charts["moving_averages"])
    plt.close(fig2)

    fig3 = plot_daily_returns(df, t, save_path=charts["daily_returns"])
    plt.close(fig3)

    fig4 = plot_return_distribution(df, t, save_path=charts["return_distribution"])
    plt.close(fig4)

    fig5 = plot_volume(df, t, save_path=charts["trading_volume"])
    plt.close(fig5)

    return charts
