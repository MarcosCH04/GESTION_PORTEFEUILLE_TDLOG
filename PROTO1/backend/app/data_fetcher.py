# backend/app/data_fetcher.py

import yfinance as yf
import pandas as pd
import json
import hashlib
from typing import List
from datetime import datetime, date
from sqlalchemy.orm import Session
from .db import SessionLocal, Base # Assumes Base is imported and defined in db.py
from .db import AssetCache # Import the model from db.py

def generate_query_hash(symbols: List[str], start_date: str, end_date: str) -> str:
    """
    Generates a unique SHA-256 hash for a yfinance query based on parameters.
    """
    # Important: Normalize the input for consistent hashing. 
    # Sort symbols alphabetically and use ISO date format.
    symbols_str = ",".join(sorted([s.upper() for s in symbols]))
    query_string = f"{symbols_str}|{start_date}|{end_date}"
    
    return hashlib.sha256(query_string.encode('utf-8')).hexdigest()


def get_prices(
    symbols: List[str],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Récupère les prix de clôture ajustés pour une liste de symboles,
    en vérifiant d'abord dans le cache (AssetCache).
    """
    if not symbols:
        return pd.DataFrame()
    
    # --- 1. Générer le Hash et Vérifier le Cache ---
    query_hash = generate_query_hash(symbols, start_date, end_date)
    
    db: Session = SessionLocal() # Get a new DB session
    
    try:
        cached_entry = db.query(AssetCache).filter(
            AssetCache.query_hash == query_hash
        ).first()

        if cached_entry:
            # Cache Hit! Update last_accessed and return data.
            cached_entry.last_accessed = datetime.utcnow()
            db.commit()
            
            # Reconstruct DataFrame from JSON
            data_dict = cached_entry.raw_data
            prices = pd.DataFrame(data_dict).rename_axis('Date')
            prices.columns.name = None
            
            # The 'Date' index is stored as string keys, so we convert them back to datetime objects
            prices.index = pd.to_datetime(prices.index)
            
            print(f"Cache Hit for {', '.join(symbols)}!")
            return prices

    except Exception as e:
        print(f"Cache lookup failed: {e}")
        db.rollback() # Don't let DB errors block fetching from yfinance
    finally:
        db.close()

    # --- 2. Cache Miss: Fetch from yfinance ---
    print(f"Cache Miss for {', '.join(symbols)}. Fetching...")
    data = yf.download(
        tickers=symbols,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )

    # ... (Rest of your existing yfinance processing logic)
    if isinstance(data.columns, pd.MultiIndex):
        close = data["Close"]
    else:
        close = data[["Close"]]
        close.columns = [symbols[0]]

    prices = close.dropna()
    
    # --- 3. Storing the Result in Cache ---
    if not prices.empty:
        # Prepare data for JSON storage: DataFrame to dictionary {date_str: {symbol: price}}
        # The key is the 'Date' and the values are the rows (symbols and prices)
        # Using to_dict('index') is a common way to serialize time-series data
        data_to_cache = prices.to_dict(orient='index')
        # Convert date objects in the index to string keys for JSON compatibility
        data_to_cache = {str(k.date()): v for k, v in data_to_cache.items()}
        
        new_cache_entry = AssetCache(
            ticker_symbol=",".join(sorted(symbols)), # Store all symbols for debug/traceability
            start_date=datetime.strptime(start_date, '%Y-%m-%d'),
            end_date=datetime.strptime(end_date, '%Y-%m-%d'),
            query_hash=query_hash,
            raw_data=data_to_cache, # Store the prepared JSON data
            last_accessed=datetime.utcnow(),
        )
        
        # Save to DB
        db_save: Session = SessionLocal()
        try:
            db_save.add(new_cache_entry)
            db_save.commit()
            print("Successfully cached data.")
        except Exception as e:
            # This handles the case where two requests try to save the same hash simultaneously
            print(f"Error saving to cache (might be duplicate): {e}")
            db_save.rollback()
        finally:
            db_save.close()

    return prices