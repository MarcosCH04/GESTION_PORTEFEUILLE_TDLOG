# — modèles Pydantic pour l’API

# Chemin d'accès: 
# backend/app/schemas.py

from typing import List, Dict, Literal
from datetime import date
from pydantic import BaseModel


class Metrics(BaseModel):
    cagr: float
    vol: float
    max_drawdown: float


class AnalyzeRequest(BaseModel):
    assets: List[str]
    start_date: date
    end_date: date


class AnalyzeResponse(BaseModel):
    prices: Dict[str, Dict[str, float]]  # date -> {symbol: price}
    metrics: Dict[str, Metrics]


class BacktestRequest(BaseModel):
    assets: List[str]
    start_date: date
    end_date: date
    invest_amount: float
    weights: List[float]
    strategy: Literal["buy_and_hold", "dca"]
    strat_start: date
    strat_end: date


class BacktestResponse(BaseModel):
    portfolio: Dict[str, float]          # date -> valeur portefeuille
    metrics: Dict[str, Metrics]
