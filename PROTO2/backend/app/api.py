# backend/app/api.py

from fastapi import APIRouter, HTTPException, Depends, Response, status
from typing import Dict, List
import json
import pandas as pd
import os
from sqlalchemy.orm import Session
from datetime import datetime

# Assuming calc.py has compute_metrics and run_backtest
from . import data_fetcher, calc 
from .schemas import (
    AnalyzeRequest, AnalyzeResponse,
    BacktestRequest, BacktestResponse,
    UserCreate, UserInDB, CaseParameters, CaseResults
)
from .auth import ( 
    create_user, get_user_by_username, verify_password, create_user_session,
    get_db, get_current_active_user_case 
)
from .db import UserCase

router = APIRouter()

# --- Utility to load list of available assets ---
def _load_assets_from_json():
    """Reads the list of available assets from assets.json."""
    here = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(here, "assets.json")
    if not os.path.exists(assets_path):
        return ["AAPL", "MSFT", "SPY", "BTC-USD"]
    with open(assets_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Utility for Robust JSON Serialization (Replacing NaN/Inf) ---
def clean_metrics_for_json(data: Dict) -> Dict:
    """Recursively replaces float('nan') and float('inf') with 0.0."""
    for k, v in data.items():
        if isinstance(v, dict):
            clean_metrics_for_json(v)
        # Check for Infinity or NaN using pd.isna for robustness
        elif v is not None and (v == float('inf') or v == float('-inf') or pd.isna(v)): 
            data[k] = 0.0 # Replaced with 0.0 as requested
    return data


# --- 1. Public Endpoints ---

@router.get("/assets")
def list_assets() -> Dict[str, list]:
    """Returns the list of available assets/tickers."""
    return {"assets": _load_assets_from_json()}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_assets(req: AnalyzeRequest, db: Session = Depends(get_db)):
    """Fetches data using the cache and calculates metrics (public access)."""
    prices = data_fetcher.get_prices(
        symbols=req.assets,
        start_date=str(req.start_date),
        end_date=str(req.end_date),
    )
    if prices.empty:
        raise HTTPException(status_code=400, detail="Impossible de récupérer les prix.")

    metrics = calc.compute_metrics(prices)
    
    # Clean metrics immediately after calculation
    metrics = clean_metrics_for_json(metrics)

    # Convert DataFrame (index=Date objects) -> dict {date_str: {symbol: price}}
    prices_dict: Dict[str, Dict[str, float]] = {}
    for dt, row in prices.iterrows():
        prices_dict[str(dt)] = {str(col): float(row[col]) for col in prices.columns}

    return AnalyzeResponse(prices=prices_dict, metrics=metrics)


# --- 2. Authentication Endpoints ---

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user."""
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    return create_user(db=db, user=user)


@router.post("/login")
def login_for_access_token(
    response: Response, 
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    """Authenticates the user, creates a session, and sets an HTTP-only cookie."""
    user = get_user_by_username(db, user_data.username)
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    # Retrieve last case for user preference persistence
    last_case = db.query(UserCase).filter(UserCase.user_id == user.id)\
                  .order_by(UserCase.last_activity_time.desc()).first()

    session = create_user_session(db, user, last_case)

    # Set the HTTP-only session cookie (secure=False for localhost testing)
    response.set_cookie(
        key="session_token",
        value=session.session_token,
        httponly=True, samesite="lax", secure=False, 
        max_age=3600*24,
    )
    
    return {"message": "Login successful", "user_id": user.id}


@router.post("/logout")
def logout(
    response: Response,
    current_case: UserCase = Depends(get_current_active_user_case),
    db: Session = Depends(get_db),
):
    """Deletes the session token from the DB and clears the client's cookie."""
    db.delete(current_case)
    db.commit()
    
    response.delete_cookie(key="session_token", httponly=True, samesite="lax", secure=False)
    
    return {"message": "Successfully logged out"}


# --- 3. Protected Endpoints ---

@router.post("/backtest", response_model=BacktestResponse)
def run_backtest_protected(
    req: BacktestRequest,
    current_session: UserCase = Depends(get_current_active_user_case), # Authentication Check
    db: Session = Depends(get_db),
):
    """Executes backtest, requiring authentication, and saves parameters/results."""
    # Redundant check, but safe to keep for basic API protection
    if len(req.assets) != len(req.weights):
        raise HTTPException(status_code=400, detail="Asset count mismatch with weights.")

    try:
        # Assumes calc.run_backtest performs weight validation and returns structured metrics
        portfolio_series, metrics = calc.run_backtest(req)
    except ValueError as e:
        # This catches the weight validation error raised in calc.py
        raise HTTPException(status_code=400, detail=str(e))

    # Clean infinite or NaN values in portfolio_series before serialization.
    if portfolio_series is not None and not portfolio_series.empty:
        portfolio_series = portfolio_series.replace([float('inf'), float('-inf'), float('nan')], 0.0)

    # Clean the metrics dictionary (solves the ValueError crash)
    if metrics is not None:
        metrics = clean_metrics_for_json(metrics)

    # Serialize portfolio series
    portfolio_dict = {str(d.date()): float(v) for d, v in portfolio_series.items()}

    # --- SAVE to UserCase (Persistence/History) ---
    try:
        # Serialize Pydantic models for database storage (JSON column)
        params_json = req.model_dump_json(exclude_unset=True) 
        
        # Ensure metrics is not None when creating CaseResults model
        results_model = CaseResults(portfolio=portfolio_dict, metrics=metrics or {}) 
        results_json = results_model.model_dump_json(exclude_unset=True)

        # Update the active session's parameters and results
        current_session.last_parameters = params_json
        current_session.calculated_results = results_json
        current_session.last_activity_time = datetime.utcnow() # Update session activity time
        db.commit()
    except Exception as e:
        print(f"Error saving session data: {e}")
        db.rollback()

    return BacktestResponse(portfolio=portfolio_dict, metrics=metrics)