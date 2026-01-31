# backend/app/api.py
from fastapi import APIRouter, HTTPException, Depends, Response, status, Request
from typing import Dict, List
import json
import os
from sqlalchemy.orm import Session 
from datetime import datetime

from . import data_fetcher, calc 
from .schemas import (
    AnalyzeRequest, AnalyzeResponse,
    BacktestRequest, BacktestResponse,
    UserCreate, UserInDB, UserStrategySchema, SaveRequest
)
from .auth import ( 
    create_user, get_user_by_username, verify_password, create_user_session,
    get_db, get_current_user 
)
from .db import User, UserStrategy, Session as SessionModel 

router = APIRouter() # Creating the API router

# --- 1. Utility ---

def _load_assets_from_json() -> list:
    """
    Reads the list of available assets from assets.json or returns defaults.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(here, "assets.json")

    if not os.path.exists(assets_path):
        return ["AAPL", "MSFT", "SPY", "BTC-USD"]
        
    try:
        with open(assets_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("assets", [])
    except Exception as e:
        # General error handling (invalid JSON, permissions, etc.)
        print(f"Error loading assets.json: {e}")
        return ["AAPL", "MSFT", "SPY"]

# --- 2. Public Endpoints ---

@router.get("/assets")
def list_assets() -> Dict[str, list]:
    """
    Returns the list of assets available for analysis.
    
    :return: Description
    :rtype: Dict[str, list] 
    """
    return {"assets": _load_assets_from_json()}

# --- 3. Authentication Endpoints ---

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user (This was the missing link causing the 404)."""
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 = Bad request (client error)
            detail="Username already registered"
        )
    return create_user(db=db, user=user)

@router.post("/login")
def login_for_access_token(
    response: Response, 
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    """ Authenticates user and creates a session cookie."""
    # Retrieve user by username
    user = get_user_by_username(db, user_data.username)

    # Verify password
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password"
        )
    # Create session and set cookie
    session = create_user_session(db, user)

    # Set HttpOnly cookie with the session token
    response.set_cookie(
        key="session_token",
        value=session.session_token,
        httponly=True, 
        samesite="lax", 
        secure=False, 
        max_age=3600*24,
    )

    # Return login success message
    return {"message": "Login successful", "user_id": user.id}

@router.post("/logout")
def logout(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ Logs out the current user by deleting the session."""
    # Retrieve session token from cookies
    token = request.cookies.get("session_token")
    # Delete session from database
    session_record = db.query(SessionModel).filter(SessionModel.session_token == token).first()
    
    if session_record:
        db.delete(session_record)
        db.commit()
    
    # Remove the cookie from the client
    response.delete_cookie(key="session_token", httponly=True, samesite="lax", secure=False)
    return {"message": "Successfully logged out"}

# --- 4. Protected Endpoints ---

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_assets(req: AnalyzeRequest,
                   current_user: User = Depends(get_current_user)):
    """
    Analyzes asset performance over a historical period
    """
    prices_df = data_fetcher.get_prices(req.assets, str(req.start_date), str(req.end_date))
    if prices_df.empty:
        raise HTTPException(status_code=400, detail="No data found for selected assets.")
    
    metrics = calc.compute_metrics(prices_df)
    # Convert DF to Dict[ISO_Date, Dict[Ticker, Price]]
    prices_dict = {str(dt): row.dropna().to_dict() for dt, row in prices_df.iterrows()}
    
    return {"prices": prices_dict, "metrics": metrics}


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest_protected(
    req: BacktestRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db),
):
    """ Executes a backtest for the current user and stores the latest run."""
    try:
        # 1. Fetch raw prices for the Asset Curves chart
        # We fetch based on the main period requested
        prices_df = data_fetcher.get_prices(
            req.assets, 
            start_date=str(req.start_date), 
            end_date=str(req.end_date)
        )

        if prices_df.empty:
            raise HTTPException(status_code=400, detail="No price data found for selected assets.")

        # 2. Run the actual backtest logic
        # Returns: (pd.Series of portfolio value, Dict of metrics)
        portfolio_series, metrics = calc.run_backtest(req)
        
    except ValueError as e:
        # Catch business logic errors (like weights not summing to 1)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch unexpected infrastructure errors
        print(f"Backtest Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during calculation.")

    # 3. Format Data for Frontend
    # Convert Portfolio Series to { "YYYY-MM-DD": value }
    portfolio_dict = {str(d): float(v) for d, v in portfolio_series.items()}

    # Convert Asset DataFrame to { "YYYY-MM-DD": { "AAPL": price, "MSFT": price } }
    asset_prices_dict = {
        str(dt): row.dropna().to_dict() 
        for dt, row in prices_df.iterrows()
    }

    # 4. Persistence: Update the 'latest_run' for this user
    # This allows the "Save Strategy" feature to work later
    latest_run = db.query(UserStrategy).filter(
        UserStrategy.user_id == current_user.id,
        UserStrategy.is_saved == False
    ).first()

    if not latest_run:
        latest_run = UserStrategy(user_id=current_user.id, 
                                  is_saved=False,
                                  name="Latest Unsaved Strategy")
        db.add(latest_run)

    # Convert the Pydantic request to a dict for JSON storage
    latest_run.parameters = json.loads(req.model_dump_json())
    latest_run.created_at = datetime.utcnow()
    
    db.commit()

    # 5. Return everything the frontend needs
    return {
        "portfolio": portfolio_dict,
        "metrics": metrics,
        "asset_prices": asset_prices_dict
    }

@router.post("/strategies/save-current")
def save_current_strategy(
    req: SaveRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """ Saves the most recent backtest as a named strategy for the user."""
    # 1. Retrieving the latest unsaved strategy
    latest = db.query(UserStrategy).filter(
        UserStrategy.user_id == current_user.id, 
        UserStrategy.is_saved == False
    ).first()
    
    if not latest or not latest.parameters:
        raise HTTPException(status_code=404, detail="No recent backtest to save.")
    
    # 2. Check storage limit (max 5 saved strategies)
    saved_count = db.query(UserStrategy).filter(
        UserStrategy.user_id == current_user.id, 
        UserStrategy.is_saved == True
    ).count()
    
    if saved_count >= 5:
        raise HTTPException(status_code=400, detail="Storage full. Delete a strategy first.")
    
    # 3. Create a new saved strategy based on the latest unsaved one 
    new_saved = UserStrategy(
        user_id=current_user.id,
        parameters=latest.parameters,
        is_saved=True,
        name=req.name
    )
    db.add(new_saved)
    db.commit()
    return {"message": "Strategy saved successfully"}

@router.get("/strategies", response_model=List[UserStrategySchema])
def get_all_my_strategies(current_user: User = Depends(get_current_user)):
    """ Retrieves all saved strategies for the current user."""
    return current_user.strategies

@router.delete("/strategies/{strategy_id}")
def delete_strategy(
    strategy_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Deletes a specific strategy owned by the current user."""
    # We filter by both ID and user_id to prevent users from deleting each other's data
    strat = db.query(UserStrategy).filter(
        UserStrategy.id == strategy_id, 
        UserStrategy.user_id == current_user.id
    ).first()
    
    if not strat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Strategy not found or you don't have permission to delete it."
        )
        
    db.delete(strat)
    db.commit()
    return {"message": "Strategy deleted successfully"}