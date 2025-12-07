# backend/app/data_fetcher.py

import yfinance as yf
import pandas as pd
from typing import List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from .db import SessionLocal, DailyPrice 


def _parse_date(date_str: str) -> date:
    """Converts a string date to a date object."""
    # Assumes input format 'YYYY-MM-DD'
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def get_prices(
    symbols: List[str],
    start_date: str,
    end_date: str,
    db: Session = None,
) -> pd.DataFrame:
    """
    Retrieves prices from the database (DailyPrice table), filling any date gaps 
    with data fetched from yfinance. We add Session for testing.
    """
    if not symbols:
        return pd.DataFrame()

    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    
    # Generate the full list of required dates
    required_dates = pd.to_datetime(pd.date_range(start_dt, end_dt, freq='D').date).normalize()
    
    if db is None:
        db = SessionLocal() # Use production session outside of tests
        close_db = True
    else:
        close_db = False # Use the test session, do not close it

    try:
        # 1. Query DB for existing data in the range
        cached_data = db.query(DailyPrice)\
            .filter(DailyPrice.ticker_symbol.in_(symbols))\
            .filter(DailyPrice.date >= start_dt)\
            .filter(DailyPrice.date <= end_dt)\
            .all()

        cached_keys = set((d.ticker_symbol, d.date) for d in cached_data)
        
        # 2. Identify missing date/ticker combinations (Gap Analysis)
        missing_keys = []
        for symbol in symbols:
            for dt in required_dates.date:
                if (symbol, dt) not in cached_keys:
                    missing_keys.append((symbol, dt))
        
        # 3. External Fetch if Gaps Exist
        if missing_keys:
            missing_symbols = sorted(list(set(k[0] for k in missing_keys)))
            fetch_start = min(k[1] for k in missing_keys)
            fetch_end = max(k[1] for k in missing_keys)
            
            # yfinance uses exclusive end dates, so fetch one day past
            yf_end_date = fetch_end + timedelta(days=1)
            
            yf_data = yf.download(
                tickers=missing_symbols,
                start=fetch_start,
                end=yf_end_date,
                auto_adjust=True,
                progress=False,
            )
            
            # 4. Process and Save New Data (Simplified for 'Close' price)
            
            close_prices = yf_data.get("Close", yf_data.get("Adj Close")) 
            new_records = []
            
            # Handle data extraction logic for single/multiple assets
            if close_prices is not None:
                prices_df = close_prices.dropna(how='all')
                
                for dt, row in prices_df.iterrows():
                    current_date = dt.normalize().date()
                    
                    for symbol in missing_symbols:
                        price = row.get(symbol)
                        if pd.notna(price) and (symbol, current_date) in missing_keys:
                            data_to_store = {"Close": float(price)} 
                            
                            new_record = DailyPrice(
                                ticker_symbol=symbol,
                                date=current_date,
                                price_data=data_to_store,
                                last_updated=datetime.utcnow()
                            )
                            new_records.append(new_record)

                if new_records:
                    db.add_all(new_records)
                    db.commit()
            
        # 5. Assemble Final DataFrame by requerying the DB
        final_data = db.query(DailyPrice)\
            .filter(DailyPrice.ticker_symbol.in_(symbols))\
            .filter(DailyPrice.date >= start_dt)\
            .filter(DailyPrice.date <= end_dt)\
            .order_by(DailyPrice.date)\
            .all()

        records = []
        for dp in final_data:
            records.append({
                'Date': dp.date,
                'Symbol': dp.ticker_symbol,
                'Close': dp.price_data.get('Close') 
            })
        
        result_df = pd.DataFrame(records)
        if result_df.empty:
             return pd.DataFrame()

        # Pivot to desired output format: index=Date, columns=Symbol
        prices = result_df.pivot(index='Date', columns='Symbol', values='Close')
        
        # Close DB session unless we are testing.
        if close_db:
             db.close()
        
        return prices.dropna(how='all')

    except Exception as e:
        print(f"Data fetching error: {e}")
        db.rollback()
        return pd.DataFrame()
    finally:
        db.close()