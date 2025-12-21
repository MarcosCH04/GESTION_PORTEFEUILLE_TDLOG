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
    UserCreate, UserInDB, UserStrategySchema
)
from .auth import ( 
    create_user, get_user_by_username, verify_password, create_user_session,
    get_db, get_current_user 
)
from .db import User, UserStrategy, Session as SessionModel 

router = APIRouter()

# --- 1. Utility ---

def _load_assets_from_json() -> list:
    """Reads the list of available assets from assets.json or returns defaults."""
    here = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(here, "assets.json")

    if not os.path.exists(assets_path):
        return ["AAPL", "MSFT", "SPY", "BTC-USD"]
        
    try:
        with open(assets_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("assets", [])
    except Exception as e:
        print(f"Error loading assets.json: {e}")
        return ["AAPL", "MSFT", "SPY"]

# --- 2. Public Endpoints ---

@router.get("/assets")
def list_assets() -> Dict[str, list]:
    return {"assets": _load_assets_from_json()}

# --- 3. Authentication Endpoints ---

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user (This was the missing link causing the 404)."""
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered"
        )
    return create_user(db=db, user=user)

@router.post("/login")
def login_for_access_token(
    response: Response, 
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    user = get_user_by_username(db, user_data.username)
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password"
        )

    session = create_user_session(db, user)

    response.set_cookie(
        key="session_token",
        value=session.session_token,
        httponly=True, 
        samesite="lax", 
        secure=False, 
        max_age=3600*24,
    )
    
    return {"message": "Login successful", "user_id": user.id}

@router.post("/logout")
def logout(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    token = request.cookies.get("session_token")
    session_record = db.query(SessionModel).filter(SessionModel.session_token == token).first()
    
    if session_record:
        db.delete(session_record)
        db.commit()
    
    response.delete_cookie(key="session_token", httponly=True, samesite="lax", secure=False)
    return {"message": "Successfully logged out"}

# --- 4. Protected Strategy Endpoints ---

@router.post("/backtest", response_model=BacktestResponse)
def run_backtest_protected(
    req: BacktestRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db),
):
    try:
        portfolio_series, metrics = calc.run_backtest(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    portfolio_dict = {str(d.date()): float(v) for d, v in portfolio_series.items()}

    latest_run = db.query(UserStrategy).filter(
        UserStrategy.user_id == current_user.id,
        UserStrategy.is_saved == False
    ).first()

    if not latest_run:
        latest_run = UserStrategy(user_id=current_user.id, is_saved=False)
        db.add(latest_run)

    latest_run.parameters = json.loads(req.model_dump_json())
    latest_run.created_at = datetime.utcnow()
    db.commit()

    return BacktestResponse(portfolio=portfolio_dict, metrics=metrics)

@router.post("/strategies/save-current")
def save_current_strategy(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    latest = db.query(UserStrategy).filter(
        UserStrategy.user_id == current_user.id, 
        UserStrategy.is_saved == False
    ).first()
    
    if not latest or not latest.parameters:
        raise HTTPException(status_code=404, detail="No recent backtest to save.")

    saved_count = db.query(UserStrategy).filter(
        UserStrategy.user_id == current_user.id, 
        UserStrategy.is_saved == True
    ).count()
    
    if saved_count >= 5:
        raise HTTPException(status_code=400, detail="Storage full. Delete a strategy first.")

    new_saved = UserStrategy(
        user_id=current_user.id,
        parameters=latest.parameters,
        is_saved=True,
        name=f"Saved Strategy {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    )
    db.add(new_saved)
    db.commit()
    return {"message": "Strategy saved successfully"}

@router.get("/strategies", response_model=List[UserStrategySchema])
def get_all_my_strategies(current_user: User = Depends(get_current_user)):
    return current_user.strategies