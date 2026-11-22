"""
Unit tests for database module.
"""

import os
import pandas as pd
import pytest
from src.database import init_db, save_stock_data, load_stock_from_db, get_records_count


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_stock.db"
    return str(db_file)


def test_init_and_save_data(temp_db):
    init_db(temp_db)
    assert os.path.exists(temp_db)

    df = pd.DataFrame({
        "Date": ["2024-01-02", "2024-01-03"],
        "Open": [100.0, 102.0],
        "High": [105.0, 106.0],
        "Low": [99.0, 101.0],
        "Close": [104.0, 105.0],
        "Adj Close": [104.0, 105.0],
        "Volume": [1000, 2000],
    })

    saved = save_stock_data(df, "AAPL", db_path=temp_db)
    assert saved == 2

    # Verify no duplicates on re-inserting the same data
    saved_again = save_stock_data(df, "AAPL", db_path=temp_db)
    assert saved_again == 2
    assert get_records_count("AAPL", db_path=temp_db) == 2

    # Query back
    loaded_df = load_stock_from_db("AAPL", db_path=temp_db)
    assert len(loaded_df) == 2
    assert "Close" in loaded_df.columns
    assert float(loaded_df["Close"].iloc[0]) == 104.0
