# — endpoints FastAPI (assets, analyze, backtest)

# Chemin d'accès:
# backend/app/api.py

from fastapi import APIRouter, HTTPException
from typing import Dict
import json
import os

from . import data_fetcher, calc
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BacktestRequest,
    BacktestResponse,
    Metrics,
)

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
        prices_dict[str(dt.date())] = {str(col): float(row[col]) for col in prices.columns}

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
