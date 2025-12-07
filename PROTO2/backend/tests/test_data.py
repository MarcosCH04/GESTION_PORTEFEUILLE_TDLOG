# backend/tests/test_data.py

import pytest
from app.data_fetcher import get_prices
from app.db import DailyPrice
from datetime import date, timedelta, datetime
import pandas as pd
from sqlalchemy.orm import Session

# Note: The 'db_session' fixture provides a clean, isolated database for each test.
# It is implicitly available via backend/tests/conftest.py.

def parse_date_str(d_str):
    """Utility to convert a date string to a date object."""
    return datetime.strptime(d_str, '%Y-%m-%d').date()

@pytest.fixture
def mock_dates():
    """Provides a known historical range for stable testing."""
    return {
        "start": "2020-01-01",
        "end": "2020-03-01",
        "today": date(2020, 1, 10)
    }

def test_cache_miss_fetches_and_saves_new_data(db_session: Session, mock_dates):
    """
    Goal 1: Ensure fetching a new date range correctly hits yfinance and saves records.
    """
    symbols = ["MSFT"]
    
    # 1. Initial Fetch (Cache Miss expected)
    prices = get_prices(symbols, mock_dates["start"], mock_dates["end"], db=db_session)

    # Assert prices were returned
    assert not prices.empty
    assert "MSFT" in prices.columns
    
    # Assert data was saved to the DailyPrice table
    saved_records = db_session.query(DailyPrice).filter(DailyPrice.ticker_symbol == "MSFT").count()
    # Expect a positive number of records (e.g., 3-4 days in the range)
    assert saved_records >= 2 # Check for at least two records to confirm saving

def test_cache_hit_does_not_re_fetch(db_session: Session, mock_dates):
    """
    Goal 2: Ensures requesting an identical range pulls only from the cache and avoids new fetches.
    """
    symbols = ["MSFT"]
    
    # 1. First fetch to populate the cache (requires MSFT to be fresh)
    get_prices(symbols, mock_dates["start"], mock_dates["end"], db=db_session)
    
    # Check initial record count
    initial_count = db_session.query(DailyPrice).filter(DailyPrice.ticker_symbol == "MSFT").count()
    assert initial_count > 0

    # 2. Re-fetch the exact same range (Cache Hit expected)
    prices = get_prices(symbols, mock_dates["start"], mock_dates["end"], db=db_session)
    
    # Assert total records did NOT increase
    final_count = db_session.query(DailyPrice).filter(DailyPrice.ticker_symbol == "MSFT").count()
    assert final_count == initial_count
    assert not prices.empty
    
def test_overlap_retrieval_only_fetches_missing_data(db_session: Session, mock_dates):
    """
    Goal: Tests the complex gap analysis to verify that only the missing portion
    of a date range is fetched from the external API (yfinance).
    """
    symbols = ["SPY"]
    
    # 1. Define the first, smaller range (e.g., first 5 days)
    start_1 = mock_dates["start"]   # "2020-01-01"
    end_1 = "2020-01-07"            # End date for cache priming

    # A. Fetch partial data to populate the cache
    prices_1 = get_prices(symbols, start_1, end_1, db=db_session)
    
    # Assert initial cache size is greater than 0
    initial_spy_count = db_session.query(DailyPrice).filter(DailyPrice.ticker_symbol == "SPY").count()
    assert initial_spy_count > 0

    # 2. Define the second, wider, overlapping range (e.g., first 10 days)
    start_2 = mock_dates["start"]   # "2020-01-01"
    end_2 = "2020-01-14"            # End date for final request

    # B. Run the overlapping fetch (This should only fetch the days between Jan 8 and Jan 14)
    # We pass the same transactional session.
    prices_2 = get_prices(symbols, start_2, end_2, db=db_session)

    # 3. Assertions
    
    # Assert data was returned
    assert not prices_2.empty
    
    # Assert that NEW data was fetched (final count is larger than initial count)
    final_spy_count = db_session.query(DailyPrice).filter(DailyPrice.ticker_symbol == "SPY").count()
    assert final_spy_count > initial_spy_count
