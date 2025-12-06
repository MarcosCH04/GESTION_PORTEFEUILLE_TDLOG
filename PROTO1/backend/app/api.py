# backend/app/api.py

from fastapi import APIRouter, HTTPException, Depends, Response, status
from typing import Dict, List
import json
import os
from sqlalchemy.orm import Session

from . import data_fetcher, calc
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BacktestRequest,
    BacktestResponse,
    Metrics,
    # New Imports for Auth
    UserCreate,
    UserInDB,
    CaseParameters,
    CaseResults,
)
from .auth import ( # Imports from your new auth.py logic
    create_user,
    get_user_by_username,
    verify_password,
    create_user_session,
    get_db,
    get_current_active_user_case,
)
from .db import UserCase # Import UserCase model for session storage

router = APIRouter()


def _load_assets_from_json():
    """
    Lit la liste des actifs disponibles dans assets.json
    (fichier simple, ex: ["AAPL", "MSFT", "SPY"]).
    """
    here = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(here, "assets.json")
    if not os.path.exists(assets_path):
        # Valeurs par défaut si le fichier n'existe pas encore
        return ["AAPL", "MSFT", "SPY", "BTC-USD"]
    with open(assets_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/assets")
def list_assets() -> Dict[str, list]:
    """
    Retourne la liste des actifs disponibles (simples tickers).
    """
    assets = _load_assets_from_json()
    return {"assets": assets}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_assets(req: AnalyzeRequest):
    """
    1) Récupère les prix via Yahoo Finance
    2) Calcule les métriques (CAGR, vol, max drawdown) sur la période donnée.
    3) Retourne les prix et les métriques.
    """
    prices = data_fetcher.get_prices(
        symbols=req.assets,
        start_date=str(req.start_date),
        end_date=str(req.end_date),
    )
    if prices.empty:
        raise HTTPException(status_code=400, detail="Impossible de récupérer les prix.")

    metrics = calc.compute_metrics(prices)

    # conversion DataFrame -> dict {date: {symbol: price}}
    prices_dict: Dict[str, Dict[str, float]] = {}
    for dt, row in prices.iterrows():
        prices_dict[str(dt)] = {str(col): float(row[col]) for col in prices.columns}

    return AnalyzeResponse(prices=prices_dict, metrics=metrics)


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest):
    """
    Exécute le backtest complet :
    - utilise les prix pour calculer le CAGR et autres métriques,
    - construit un portefeuille synthétique sur la période de stratégie.
    """
    if len(req.assets) != len(req.weights):
        raise HTTPException(
            status_code=400,
            detail="Le nombre d'actifs ne correspond pas au nombre de poids."
        )

    try:
        portfolio_series, metrics = calc.run_backtest(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    portfolio_dict = {str(d.date()): float(v) for d, v in portfolio_series.items()}

    return BacktestResponse(
        portfolio=portfolio_dict,
        metrics=metrics,
    )

## --- NEW: AUTHENTICATION ENDPOINTS ---

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user after checking for username uniqueness."""
    
    # 1. Check if user already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 2. Create and save the new user (password is hashed internally)
    new_user = create_user(db=db, user=user)
    return new_user


@router.post("/login")
def login_for_access_token(
    response: Response, 
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Authenticates the user, creates a session, and sets an HTTP-only cookie.
    """
    user = get_user_by_username(db, user_data.username)
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # 1. Get the last saved case/parameters for this user (if any)
    # This helps pre-load the user's last setup on login
    last_case = db.query(UserCase).filter(UserCase.user_id == user.id)\
                  .order_by(UserCase.last_activity_time.desc()).first()

    # 2. Create a new UserCase entry (which includes the session_token)
    session = create_user_session(db, user, last_case)

    # 3. Set the HTTP-only session cookie
    # secure=True should be used in production (HTTPS)
    # samesite='lax' is recommended for modern web
    response.set_cookie(
        key="session_token",
        value=session.session_token,
        httponly=True,  # Crucial: prevents client-side JS access (XSS defense)
        samesite="lax", 
        secure=False,   # Set to True in production!
        max_age=3600*24, # Cookie lasts a long time, but session check handles expiration
    )
    
    # Return basic user info or a success message
    return {"message": "Login successful", "user_id": user.id}


@router.post("/logout")
def logout(
    response: Response,
    # Requires a valid session cookie to look up the case and expire it.
    current_case: UserCase = Depends(get_current_active_user_case),
    db: Session = Depends(get_db),
):
    """Deletes the session token from the DB and clears the client's cookie."""
    
    # 1. Delete the session record from the database (server-side cleanup)
    db.delete(current_case)
    db.commit()
    
    # 2. Clear the session cookie on the client side
    response.delete_cookie(
        key="session_token",
        httponly=True,
        samesite="lax",
        secure=False, # Set to True in production!
    )
    
    return {"message": "Successfully logged out"}


## --- UPDATED: PROTECTED ENDPOINTS ---

@router.post("/backtest", response_model=BacktestResponse)
def run_backtest_protected(
    req: BacktestRequest,
    current_session: UserCase = Depends(get_current_active_user_case), # PROTECTION
    db: Session = Depends(get_db), # Required for saving/updating session
):
    """
    Exécute le backtest et met à jour les paramètres et résultats de la session utilisateur.
    """
    if len(req.assets) != len(req.weights):
        raise HTTPException(
            status_code=400,
            detail="Le nombre d'actifs ne correspond pas au nombre de poids."
        )

    try:
        portfolio_series, metrics = calc.run_backtest(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    portfolio_dict = {str(d.date()): float(v) for d, v in portfolio_series.items()}

    # --- SAVE to UserCase (Session) ---
    try:
        # Pydantic models to JSON strings for database storage
        params_json = req.model_dump_json(exclude_unset=True) 
        results_model = CaseResults(portfolio=portfolio_dict, metrics=metrics)
        results_json = results_model.model_dump_json(exclude_unset=True)

        # Update the current active session's parameters and results
        current_session.last_parameters = params_json
        current_session.calculated_results = results_json
        
        # NOTE: last_activity_time is updated automatically by the dependency checker
        db.commit()
    except Exception as e:
        # Log the error but don't fail the backtest operation
        print(f"Error saving session data: {e}")
        db.rollback()

    return BacktestResponse(
        portfolio=portfolio_dict,
        metrics=metrics,
    )


