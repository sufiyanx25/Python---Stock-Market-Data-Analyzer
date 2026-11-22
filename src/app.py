"""
app.py

Streamlit Web Dashboard for Stock Market Data Analyzer.
Provides a modern, interactive, and beginner-friendly web UI.

Includes 10 Core Sections:
1. Dashboard Overview
2. Stock Selection
3. Historical Stock Data
4. Price Trend Analysis
5. Moving Average Analysis
6. Daily Returns Analysis
7. Risk and Volatility Analysis
8. Data Table
9. Analysis Summary
10. Download Reports
"""

import os
import sys
from datetime import date, timedelta
import pandas as pd
import streamlit as st

# Ensure project root is in sys.path when running from src or workspace root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
from src.visualization import (
    plot_closing_price,
    plot_moving_averages,
    plot_daily_returns,
    plot_return_distribution,
    plot_volume,
    save_all_charts,
)
from src.database import (
    init_db,
    save_stock_data,
    load_stock_from_db,
    get_available_tickers,
    get_records_count,
)
from src.report_generator import (
    generate_text_report,
    save_text_report,
    export_cleaned_csv,
    generate_csv_download,
    generate_txt_download,
)


# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Stock Market Data Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid #E2E8F0;
    }
    .disclaimer-box {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #92400E;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    # Initialize SQLite database
    init_db()

    # ---------------------------------------------------------
    # Section 1: Dashboard Overview
    # ---------------------------------------------------------
    st.markdown('<div class="main-header">📈 Stock Market Data Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">An interactive quantitative analysis platform for historical equity data, technical indicators, risk assessment, and reporting.</div>',
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Section 2: Stock Selection (Sidebar Controls)
    # ---------------------------------------------------------
    st.sidebar.header("⚙️ Data Source & Parameters")

    data_source = st.sidebar.radio(
        "Choose Data Source:",
        ("Online Yahoo Finance (yfinance)", "CSV Upload / Local Sample"),
        index=0,
    )

    ticker = "AAPL"
    raw_df = None
    fetch_success = False

    if data_source == "Online Yahoo Finance (yfinance)":
        ticker_input = st.sidebar.text_input(
            "Stock Ticker Symbol:",
            value="AAPL",
            help="Enter a stock ticker (e.g. AAPL, MSFT, GOOGL, NVDA, RELIANCE.NS)",
        ).strip().upper()

        st.sidebar.caption("Quick picks: AAPL | MSFT | GOOGL | TSLA | RELIANCE.NS")

        # Date Pickers
        col_d1, col_d2 = st.sidebar.columns(2)
        today = date.today()
        one_year_ago = today - timedelta(days=365)

        start_date = col_d1.date_input("Start Date", one_year_ago)
        end_date = col_d2.date_input("End Date", today)

        fetch_button = st.sidebar.button("📥 Fetch Stock Data", use_container_width=True)

        # Session state persistence
        if fetch_button or "stock_df" not in st.session_state:
            if not validate_ticker(ticker_input):
                st.sidebar.error("⚠️ Invalid ticker symbol format.")
            elif start_date >= end_date:
                st.sidebar.error("⚠️ Start date must be earlier than end date.")
            else:
                with st.spinner(f"Fetching online market data for {ticker_input}..."):
                    try:
                        raw_df = fetch_stock_data(ticker_input, start_date=start_date, end_date=end_date)
                        st.session_state["raw_df"] = raw_df
                        st.session_state["ticker"] = ticker_input
                        fetch_success = True
                    except Exception as err:
                        st.sidebar.error(f"Error fetching data: {err}")
                        st.sidebar.info("💡 You can switch to CSV Upload fallback below.")

    else:
        # CSV Upload / Local Sample Fallback
        csv_option = st.sidebar.radio(
            "CSV Source:",
            ("Use Built-in Sample (data/sample_stock_data.csv)", "Upload CSV File"),
        )

        ticker_input = st.sidebar.text_input("Ticker Name for CSV:", value="SAMPLE").strip().upper()

        if csv_option == "Use Built-in Sample (data/sample_stock_data.csv)":
            sample_path = os.path.join(PROJECT_ROOT, "data", "sample_stock_data.csv")
            if os.path.exists(sample_path):
                raw_df = load_csv_data(sample_path)
                st.session_state["raw_df"] = raw_df
                st.session_state["ticker"] = ticker_input or "SAMPLE"
                fetch_success = True
            else:
                st.sidebar.error("Sample CSV file not found.")
        else:
            uploaded_file = st.sidebar.file_uploader("Upload CSV file:", type=["csv"])
            if uploaded_file is not None:
                try:
                    raw_df = load_csv_data(uploaded_file)
                    st.session_state["raw_df"] = raw_df
                    st.session_state["ticker"] = ticker_input or "UPLOADED"
                    fetch_success = True
                except Exception as err:
                    st.sidebar.error(f"Failed to load CSV: {err}")

    # Retrieve current active DataFrame from session state
    if "raw_df" in st.session_state and st.session_state["raw_df"] is not None:
        raw_df = st.session_state["raw_df"]
        ticker = st.session_state.get("ticker", "STOCK")
        fetch_success = True

    # Show database stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗄️ SQLite Database Status")
    db_records = get_records_count()
    saved_tickers = get_available_tickers()
    st.sidebar.write(f"Total Stored Records: **{db_records}**")
    if saved_tickers:
        st.sidebar.caption(f"Stored Tickers: {', '.join(saved_tickers)}")

    # Guard: Require data to proceed
    if not fetch_success or raw_df is None or raw_df.empty:
        st.info("👈 Please select a stock ticker or upload a CSV file in the sidebar to begin analysis.")
        return

    # ---------------------------------------------------------
    # Clean and Process Data
    # ---------------------------------------------------------
    try:
        cleaned_df = clean_stock_data(raw_df)
        is_valid, validation_msg = validate_cleaned_data(cleaned_df)
        if not is_valid:
            st.error(f"Data validation failed: {validation_msg}")
            return
    except Exception as clean_err:
        st.error(f"Error during data cleaning: {clean_err}")
        return

    # Calculate returns, moving averages, and metrics
    processed_df = calculate_daily_returns(cleaned_df)
    processed_df = calculate_moving_averages(processed_df, 20, 50)
    metrics = compute_summary_metrics(processed_df, ticker=ticker)

    # ---------------------------------------------------------
    # Section 3: Historical Stock Data & Key Metrics
    # ---------------------------------------------------------
    st.subheader(f"📊 Key Performance Metrics: {ticker}")

    m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

    latest_price = metrics["latest_close"]
    first_price = metrics["first_close"]
    tot_change_pct = metrics["total_return_pct"]
    daily_ret = metrics["avg_daily_return_pct"]
    high_price = metrics["highest_close"]
    low_price = metrics["lowest_close"]
    ann_vol = metrics["annualized_volatility_pct"]
    avg_vol = metrics["avg_volume"]

    m_col1.metric("Latest Close", f"${latest_price:,.2f}", f"{tot_change_pct:+.2f}% total")
    m_col2.metric("Period High", f"${high_price:,.2f}")
    m_col3.metric("Period Low", f"${low_price:,.2f}")
    m_col4.metric("Avg Daily Return", f"{daily_ret:+.2f}%")
    m_col5.metric("Annualized Volatility", f"{ann_vol:.2f}%")
    m_col6.metric("Avg Daily Volume", f"{avg_vol:,.0f}")

    st.markdown("---")

    # ---------------------------------------------------------
    # Section 4: Price Trend Analysis
    # ---------------------------------------------------------
    st.subheader("📈 Price Trend Analysis")
    st.caption(f"Historical closing price movement for {ticker} from {metrics['start_date']} to {metrics['end_date']}.")
    fig_price = plot_closing_price(processed_df, ticker)
    st.pyplot(fig_price)

    # ---------------------------------------------------------
    # Section 5: Moving Average Analysis
    # ---------------------------------------------------------
    st.subheader("📉 Moving Average Trend Analysis (SMA 20 & SMA 50)")
    st.caption("Moving averages smooth out day-to-day noise to highlight overarching trend direction.")
    fig_ma = plot_moving_averages(processed_df, ticker)
    st.pyplot(fig_ma)

    # Educational Moving Average Insight
    trend_obs = metrics["trend_observation"]
    st.info(f"**Technical Posture:** {trend_obs}. A 20-day Simple Moving Average tracks short-term momentum, while the 50-day Simple Moving Average represents intermediate-term trend support.")

    # ---------------------------------------------------------
    # Section 6: Daily Returns Analysis
    # ---------------------------------------------------------
    st.subheader("📊 Daily Percentage Returns")
    st.caption("Distribution of positive (green) and negative (red) trading day returns over time.")
    fig_ret = plot_daily_returns(processed_df, ticker)
    st.pyplot(fig_ret)

    # ---------------------------------------------------------
    # Section 7: Risk and Volatility Analysis
    # ---------------------------------------------------------
    st.subheader("⚖️ Risk and Volatility Analysis")
    col_v1, col_v2 = st.columns([2, 1])

    with col_v1:
        fig_dist = plot_return_distribution(processed_df, ticker)
        st.pyplot(fig_dist)

    with col_v2:
        st.markdown("#### Volatility Breakdown")
        st.write(f"- **Daily Volatility (Std Dev):** {metrics['daily_volatility_pct']:.2f}%")
        st.write(f"- **Annualized Volatility:** {ann_vol:.2f}%")
        st.write(f"- **Total Trading Sessions:** {metrics['total_trading_days']} days")
        st.caption(
            "Annualized volatility represents the estimated annualized standard deviation of daily percentage price returns "
            "(calculated using 252 standard trading days per year: $\\sigma_{annual} = \\sigma_{daily} \\times \\sqrt{252}$)."
        )

    # ---------------------------------------------------------
    # Trading Volume Section
    # ---------------------------------------------------------
    st.subheader("📦 Trading Volume Analysis")
    fig_vol = plot_volume(processed_df, ticker)
    st.pyplot(fig_vol)

    st.markdown("---")

    # ---------------------------------------------------------
    # Section 8: Data Table
    # ---------------------------------------------------------
    st.subheader("📋 Cleaned Historical Data Table")
    st.caption("Preview of processed records with technical indicators.")

    # Format display columns
    display_df = processed_df.copy()
    display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True, height=280)

    # ---------------------------------------------------------
    # Section 9: Analysis Summary & SQLite Persistence
    # ---------------------------------------------------------
    st.subheader("📝 Automated Analysis Summary")
    summary_text = generate_text_summary(metrics)
    st.text_area("Generated Technical & Performance Summary", summary_text, height=220)

    # Database Persistence Action
    col_db1, col_db2 = st.columns([2, 3])
    with col_db1:
        if st.button("💾 Save Data to SQLite Database", use_container_width=True):
            saved_count = save_stock_data(processed_df, ticker)
            st.success(f"Successfully saved {saved_count} records for {ticker} into SQLite database!")

    # ---------------------------------------------------------
    # Section 10: Download Reports & Exports
    # ---------------------------------------------------------
    st.subheader("📥 Export & Download Reports")
    st.caption("Export cleaned datasets, formatted text reports, or save generated charts to disk.")

    report_content = generate_text_report(metrics, processed_df)
    csv_bytes = generate_csv_download(processed_df)
    txt_bytes = generate_txt_download(report_content)

    d_col1, d_col2, d_col3 = st.columns(3)

    with d_col1:
        st.download_button(
            label="📄 Download Cleaned CSV",
            data=csv_bytes,
            file_name=f"{ticker}_cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with d_col2:
        st.download_button(
            label="📑 Download Summary Report (TXT)",
            data=txt_bytes,
            file_name=f"{ticker}_analysis_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with d_col3:
        if st.button("💾 Save Charts & Reports to Disk", use_container_width=True):
            chart_paths = save_all_charts(processed_df, ticker)
            saved_txt = save_text_report(report_content, ticker)
            saved_csv = export_cleaned_csv(processed_df, ticker)
            st.success(f"Saved 5 charts to 'outputs/charts/' and reports to 'outputs/reports/'!")

    # ---------------------------------------------------------
    # Educational Disclaimer
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="disclaimer-box">
            <strong>⚠️ Educational Disclaimer:</strong><br>
            This project is intended for educational and analytical purposes only. It does not provide financial advice or investment recommendations.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
