# backend/app/data_fetcher.py

import yfinance as yf
import pandas as pd
from typing import List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from .db import SessionLocal, DailyPrice 

# Utility to convert string dates to datetime objects (used internally)
def _parse_date(date_str: str) -> date:
    # Assumes input format 'YYYY-MM-DD'
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def get_prices(
    symbols: List[str],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Retrieves prices from the database, filling any date gaps with data from yfinance.
    """
    if not symbols:
        return pd.DataFrame()

    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    
    # Generate the full list of required dates between start_dt and end_dt (inclusive)
    required_dates = pd.to_datetime(pd.date_range(start_dt, end_dt, freq='D').date).normalize()
    
    db: Session = SessionLocal()
    
    try:
        # --- 1. Check Cache for Existing Data ---
        # Query the database for all available data within the required range
        cached_data = db.query(DailyPrice)\
            .filter(DailyPrice.ticker_symbol.in_(symbols))\
            .filter(DailyPrice.date >= start_dt)\
            .filter(DailyPrice.date <= end_dt)\
            .all()

        # Build a set of (ticker, date) tuples for quick lookup
        cached_keys = set((d.ticker_symbol, d.date) for d in cached_data)

        # --- 2. Determine Missing Keys (Gap Analysis) ---
        
        missing_keys = []
        for symbol in symbols:
            for dt in required_dates.date:
                if (symbol, dt) not in cached_keys:
                    missing_keys.append((symbol, dt))
        
        # Determine the earliest and latest date we need to fetch externally
        if missing_keys:
            missing_symbols = sorted(list(set(k[0] for k in missing_keys)))
            fetch_start = min(k[1] for k in missing_keys)
            fetch_end = max(k[1] for k in missing_keys)
            
            print(f"Cache Miss. Missing data for {len(missing_keys)} days between {fetch_start} and {fetch_end}. Fetching...")
        else:
            print("Cache Hit! All data is present in the database.")
            # If nothing is missing, skip the fetch and jump straight to assembly.
            fetch_start = fetch_end = None
            missing_symbols = []

        # --- 3. External Fetch (Only if Gaps Exist) ---
        new_records = []
        if fetch_start and missing_symbols:
            # We fetch one day past the end date, as yfinance uses exclusive end dates
            yf_end_date = fetch_end + timedelta(days=1)
            
            # Fetch data from Yahoo Finance
            yf_data = yf.download(
                tickers=missing_symbols,
                start=fetch_start,
                end=yf_end_date,
                auto_adjust=True,
                progress=False,
            )
            
            # --- 4. Process and Save New Data ---
            
            # Use 'Close' price for the calculation, or customize this if calc.py needs other columns
            close_prices = yf_data.get("Close", yf_data.get("Adj Close")) 

            if close_prices is None:
                # Handle single asset case where the column name might be the symbol
                if len(missing_symbols) == 1 and missing_symbols[0] in yf_data.columns.names:
                     close_prices = yf_data[missing_symbols[0]].get("Close")

            if close_prices is not None:
                prices_df = close_prices.dropna(how='all')
                
                for dt, row in prices_df.iterrows():
                    current_date = dt.normalize().date()
                    
                    for symbol in missing_symbols:
                        # Ensure the key we are looking for was actually a missing date
                        if (symbol, current_date) in missing_keys:
                            
                            # Extract relevant data for JSON storage
                            # Only store the date if it's within the requested range and price is valid
                            price = row.get(symbol)
                            if pd.notna(price):
                                # Save the closing price and maybe volume/high/low if needed later
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
                    print(f"Successfully saved {len(new_records)} new daily records.")
            
        # --- 5. Assemble Final DataFrame (Re-query all data, including new and old) ---
        
        # Fetch ALL required data from the database again
        final_data = db.query(DailyPrice)\
            .filter(DailyPrice.ticker_symbol.in_(symbols))\
            .filter(DailyPrice.date >= start_dt)\
            .filter(DailyPrice.date <= end_dt)\
            .order_by(DailyPrice.date)\
            .all()

        # Convert final_data list to a pandas DataFrame
        records = []
        for dp in final_data:
            records.append({
                'Date': dp.date,
                'Symbol': dp.ticker_symbol,
                'Close': dp.price_data.get('Close') # Extract the key data point
            })
        
        result_df = pd.DataFrame(records)
        if result_df.empty:
             return pd.DataFrame()

        # Pivot to desired output format: index=Date, columns=Symbol
        prices = result_df.pivot(index='Date', columns='Symbol', values='Close')
        
        return prices.dropna(how='all')

    except Exception as e:
        print(f"Data fetching error: {e}")
        db.rollback()
        # Fallback: Consider fetching from yfinance directly here if the database operation fails critically
        # For now, return an empty DataFrame or re-raise the error.
        return pd.DataFrame()
    finally:
        db.close()