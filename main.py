"""
main.py

Stock Market Data Analyzer - Main CLI Entry Point.

Coordinates the complete data processing pipeline:
1. Data collection (Yahoo Finance fetch or local sample CSV fallback)
2. Data cleaning and schema validation
3. Quantitative analysis (returns, moving averages, volatility)
4. Persistence into SQLite database
5. Generation of professional charts inside outputs/charts/
6. Generation of comprehensive reports inside outputs/reports/
7. Guidance on launching the interactive Streamlit dashboard
"""

import os
import sys
from datetime import date, timedelta

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_fetcher import fetch_stock_data, load_csv_data, validate_ticker
from src.data_cleaner import clean_stock_data, validate_cleaned_data
from src.analysis import (
    calculate_daily_returns,
    calculate_moving_averages,
    compute_summary_metrics,
    generate_text_summary,
)
from src.visualization import save_all_charts
from src.database import init_db, save_stock_data, get_records_count
from src.report_generator import generate_text_report, save_text_report, export_cleaned_csv


def print_banner():
    banner = """
======================================================================
               📈 STOCK MARKET DATA ANALYZER (CLI)
======================================================================
    An end-to-end Python pipeline for historical market analysis,
    technical indicators, risk profiling, SQLite, and reporting.
======================================================================
"""
    print(banner)


def run_pipeline(ticker: str = "AAPL", use_sample: bool = False):
    """
    Run complete analytical pipeline for a given ticker or local sample dataset.
    """
    print(f"[*] Starting analysis pipeline for: {ticker}")

    # Step 1: Initialize Database
    init_db()
    print("[+] SQLite database initialized.")

    # Step 2: Ingest Data
    raw_df = None
    if not use_sample:
        today = date.today()
        one_year_ago = today - timedelta(days=365)
        print(f"[*] Fetching historical market data from Yahoo Finance ({one_year_ago} to {today})...")
        try:
            raw_df = fetch_stock_data(ticker, start_date=one_year_ago, end_date=today)
            print(f"[+] Downloaded {len(raw_df)} trading records for {ticker}.")
        except Exception as err:
            print(f"[!] Warning: Online fetch failed ({err}).")
            print("[*] Falling back to local sample dataset: data/sample_stock_data.csv")
            sample_csv = os.path.join(PROJECT_ROOT, "data", "sample_stock_data.csv")
            raw_df = load_csv_data(sample_csv)
            ticker = "SAMPLE"
    else:
        sample_csv = os.path.join(PROJECT_ROOT, "data", "sample_stock_data.csv")
        raw_df = load_csv_data(sample_csv)
        ticker = "SAMPLE"
        print(f"[+] Loaded {len(raw_df)} records from local sample dataset.")

    # Step 3: Clean and Validate Data
    print("[*] Cleaning and validating dataset...")
    cleaned_df = clean_stock_data(raw_df)
    is_valid, msg = validate_cleaned_data(cleaned_df)
    if not is_valid:
        print(f"[!] Data validation failed: {msg}")
        return False
    print(f"[+] Data cleaned successfully ({len(cleaned_df)} valid trading sessions).")

    # Step 4: Quantitative Analysis & Indicators
    print("[*] Computing technical indicators and summary metrics...")
    processed_df = calculate_daily_returns(cleaned_df)
    processed_df = calculate_moving_averages(processed_df, 20, 50)
    metrics = compute_summary_metrics(processed_df, ticker=ticker)

    # Step 5: Display Summary
    print("\n" + "=" * 60)
    print(generate_text_summary(metrics))
    print("=" * 60 + "\n")

    # Step 6: Save into SQLite Database
    print("[*] Persisting records into SQLite database (data/stock_database.db)...")
    records_saved = save_stock_data(processed_df, ticker)
    total_in_db = get_records_count(ticker)
    print(f"[+] Saved {records_saved} records. Total records for {ticker} in DB: {total_in_db}.")

    # Step 7: Generate and Save Visual Charts
    print("[*] Generating charts in outputs/charts/...")
    charts = save_all_charts(processed_df, ticker)
    for name, path in charts.items():
        print(f"    - Saved chart: {os.path.basename(path)}")

    # Step 8: Generate and Save Reports
    print("[*] Generating reports in outputs/reports/...")
    report_text = generate_text_report(metrics, processed_df)
    report_path = save_text_report(report_text, ticker)
    csv_path = export_cleaned_csv(processed_df, ticker)
    print(f"    - Saved report: {os.path.basename(report_path)}")
    print(f"    - Saved cleaned CSV: {os.path.basename(csv_path)}")

    # Step 9: Completed
    print("\n[✔] Analysis Pipeline completed successfully!")
    print("\nTo launch the interactive Streamlit Web Dashboard, run:")
    print("    streamlit run src/app.py\n")
    return True


def main():
    print_banner()

    # Read optional CLI ticker argument
    ticker = "AAPL"
    if len(sys.argv) > 1:
        ticker = sys.argv[1].strip().upper()

    try:
        run_pipeline(ticker=ticker)
    except KeyboardInterrupt:
        print("\n[!] Execution interrupted by user.")
    except Exception as exc:
        print(f"\n[!] Unexpected error: {exc}")


if __name__ == "__main__":
    main()
