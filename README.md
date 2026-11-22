# Stock Market Data Analyzer

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An end-to-end, beginner-friendly financial data analysis and visualization system built with Python, Pandas, NumPy, yfinance, Matplotlib, Seaborn, SQLite, and Streamlit.

---

## 📌 Project Overview & Problem Statement

Retail investors, finance students, and beginner programmers often face hurdles when attempting to ingest, clean, and quantitatively evaluate historical stock data. Financial data is frequently fragmented, contains missing or irregular trading session timestamps, and requires non-trivial technical computations (e.g. log/percentage returns, moving average smoothing, annualized volatility scaling).

The **Stock Market Data Analyzer** solves this problem by providing a modular, reliable, and completely local analytical pipeline that:
1. Automatically retrieves real-world market data via `yfinance` with fallback to local CSV uploads.
2. Performs automated data validation, cleaning, and chronological deduplication.
3. Calculates standard quantitative and technical indicators (SMA 20, SMA 50, Daily Returns, Annualized Volatility).
4. Persists market history into an SQLite database with duplicate prevention.
5. Generates high-resolution visualization charts and downloadable summary reports.
6. Delivers an interactive, beginner-friendly web dashboard powered by Streamlit.

---

## 🚀 Core Features

- **Automated Data Ingestion**:
  - Live market data fetching for any global equity ticker (e.g., `AAPL`, `MSFT`, `GOOGL`, `RELIANCE.NS`) via `yfinance`.
  - Flexible user-selected start and end dates.
  - Built-in CSV file upload and local sample fallback (`data/sample_stock_data.csv`) for offline use.
  - Robust ticker validation and network error handling.
- **Robust Data Cleaning Pipeline**:
  - Standardizes irregular column names across different data providers.
  - Formats and validates dates into chronological order.
  - Deduplicates overlapping date timestamps.
  - Forward-fills and backward-fills missing price observations.
  - Converts columns to valid numeric types and formats trading volume as integer.
- **Quantitative & Technical Analysis**:
  - Daily percentage returns.
  - 20-day Simple Moving Average (SMA 20) for short-term trend momentum.
  - 50-day Simple Moving Average (SMA 50) for medium-term trend support.
  - Annualized Volatility ($\sigma_{annual} = \sigma_{daily} \times \sqrt{252}$).
  - Period highest, lowest, and latest closing prices.
  - Period cumulative returns and average daily trading volume.
- **Professional Data Visualizations**:
  - Historical closing price trend with shaded area.
  - Price trend with SMA 20 and SMA 50 overlays.
  - Daily percentage return bar chart with zero-baseline and green/red highlights.
  - Return distribution histogram with Kernel Density Estimation (KDE) and standard deviation bounds.
  - Trading volume bar chart with rolling average line.
- **SQLite Database Persistence**:
  - Stores ticker, date, open, high, low, close, adjusted close, and volume.
  - Prevents duplicate records using a `UNIQUE(ticker, date)` constraint.
  - Allows querying historical data and viewing database metrics directly.
- **Automated Reporting & Exports**:
  - Export cleaned data to CSV.
  - Export factual, text-based performance reports in TXT format.
  - Save all generated charts directly to `outputs/charts/`.
  - Save generated summary reports to `outputs/reports/`.
- **Interactive Streamlit Web Dashboard**:
  - Modern, 10-section responsive user interface with real-time metric cards, interactive charts, data table inspection, and one-click download buttons.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core language for analysis and application logic |
| **Data Processing** | Pandas, NumPy | DataFrames, data cleaning, and vectorized arithmetic |
| **Market Data** | yfinance | Yahoo Finance historical data ingestion |
| **Visualization** | Matplotlib, Seaborn | Static and publication-quality financial charts |
| **Database** | SQLite3 | Local relational storage with duplicate constraints |
| **Web Dashboard** | Streamlit | Interactive, reactive graphical user interface |
| **Testing** | Pytest | Automated unit and integration testing suite |

---

## 📂 Project Folder Structure

```
Stock-Market-Data-Analyzer/
├── data/
│   ├── sample_stock_data.csv       # Built-in sample stock dataset
│   └── stock_database.db           # SQLite database file (created on runtime)
├── notebooks/                      # Exploratory data analysis notebooks
├── src/
│   ├── __init__.py                 # Package initializer
│   ├── data_fetcher.py             # Data collection from yfinance & CSV
│   ├── data_cleaner.py             # Preprocessing, schema validation & cleaning
│   ├── analysis.py                 # Returns, moving averages, and volatility
│   ├── visualization.py            # Matplotlib & Seaborn chart generators
│   ├── report_generator.py         # TXT & CSV report generation
│   ├── database.py                 # SQLite database storage & query operations
│   └── app.py                      # 10-section Streamlit web dashboard
├── outputs/
│   ├── charts/                     # Generated PNG charts
│   └── reports/                    # Generated TXT reports and cleaned CSVs
├── tests/
│   ├── test_data_cleaner.py        # Data cleaning unit tests
│   ├── test_analysis.py            # Quantitative calculation tests
│   └── test_database.py            # Database storage and deduplication tests
├── images/                         # Project screenshots & graphics
├── docs/                           # Documentation and guides
├── README.md                       # Comprehensive project documentation
├── requirements.txt                # Python project dependencies
├── .gitignore                      # Git exclusion rules
└── main.py                         # CLI application entry point
```

---

## ⚙️ Installation Instructions

### 1. Clone or Open the Repository
```bash
cd "c:\Users\Sufff_x25\Desktop\Python - Stock Market Data Analyzer"
```

### 2. Create and Activate a Virtual Environment
- **On Windows (PowerShell / Command Prompt)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **On macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚦 How to Run the Application

### Option A: Interactive Streamlit Web Dashboard (Recommended)
Launch the modern 10-section web dashboard:
```bash
streamlit run src/app.py
```
Then open your web browser at `http://localhost:8501`.

### Option B: Command-Line Interface (CLI Pipeline)
Run the full end-to-end analytical pipeline from the terminal:
```bash
# Analyze default ticker (AAPL) or fallback to local sample:
python main.py

# Or analyze any custom stock ticker:
python main.py MSFT
```

### Option C: Run Automated Tests
Execute the unit test suite:
```bash
pytest -v
```

---

## 📸 Sample Screenshots Section

The Streamlit dashboard comprises 10 comprehensive analytical sections:

1. **Dashboard Overview**: Header banner with instructions and description.
2. **Stock Selection & Sidebar**: Real-time ticker search, date pickers, CSV upload fallback, and database stats.
3. **Historical Stock Data & Key Metrics**: Real-time metrics displaying Latest Price, Period High, Period Low, Total Return, Daily Return, and Volume.
4. **Price Trend Analysis**: High-resolution closing price line chart with filled gradient.
5. **Moving Average Analysis**: SMA 20 (short-term) and SMA 50 (medium-term) trend overlays with educational commentary.
6. **Daily Returns Analysis**: Color-coded bar chart (green for positive days, red for negative days).
7. **Risk & Volatility Analysis**: Return distribution histogram with KDE overlay, mean, and standard deviation bounds.
8. **Trading Volume Analysis**: Historical trading activity with 20-day moving average volume.
9. **Cleaned Data Table & SQLite Persistence**: Interactive table viewer with pagination and one-click database save button.
10. **Report Downloads**: One-click download buttons for cleaned CSV and TXT reports, plus export of all charts to `outputs/charts/`.

---

## 📊 Expected Outputs

When running the CLI or clicking **"Save Charts & Reports to Disk"** in the web dashboard, the following files are produced:

- **Outputs in `outputs/charts/`**:
  - `{TICKER}_closing_price.png`
  - `{TICKER}_moving_averages.png`
  - `{TICKER}_daily_returns.png`
  - `{TICKER}_return_distribution.png`
  - `{TICKER}_trading_volume.png`
- **Outputs in `outputs/reports/`**:
  - `{TICKER}_analysis_report.txt` (Comprehensive factual performance summary)
  - `{TICKER}_cleaned_data.csv` (Standardized dataset ready for further analysis)
- **Outputs in `data/`**:
  - `stock_database.db` (Persistent SQLite relational database)

---

## 🎓 Learning Outcomes for Beginner Students

By studying and using this project, beginner Python students learn:
1. **API Integration**: How to interact with real-world financial APIs using `yfinance`.
2. **Data Wrangling**: How to clean messy time series data, handle missing values, and deduplicate timestamps using `pandas`.
3. **Financial Mathematics**: How to compute daily percentage returns, rolling moving averages, and annualize daily volatility ($\sigma \times \sqrt{252}$).
4. **Data Visualization**: How to produce publication-grade statistical charts using `matplotlib` and `seaborn`.
5. **Database Engineering**: How to initialize relational schemas in SQLite, enforce constraints (`UNIQUE(ticker, date)`), and query data into DataFrames.
6. **Web App Development**: How to build reactive, full-featured dashboards using `streamlit`.
7. **Modular Software Architecture**: How to organize code cleanly into modules (`src/`), separate concerns, and write automated tests with `pytest`.

---

## ⚠️ Educational Disclaimer

> **This project is intended for educational and analytical purposes only. It does not provide financial advice or investment recommendations.**
