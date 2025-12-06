# — modèles Pydantic pour l’API

# Chemin d'accès: 
# backend/app/schemas.py

from typing import List, Dict, Literal, Optional
from datetime import date, datetime
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


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str # This should be hashed before saving to DB!

class UserInDB(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CaseParameters(BaseModel):
    """
    Model to structure the data stored in the 'last_parameters' JSON field.
    Based on BacktestRequest, but can be stripped down if necessary.
    """
    assets: List[str]
    start_date: date
    end_date: date
    invest_amount: float
    weights: List[float]
    strategy: Literal["buy_and_hold", "dca"]
    strat_start: date
    strat_end: date

class CaseResults(BaseModel):
    """
    Model to structure the data stored in the 'calculated_results' JSON field.
    Based on BacktestResponse.
    """
    portfolio: Dict[str, float]
    metrics: Dict[str, Metrics]


class UserCaseBase(BaseModel):
    is_favorite: bool = False
    case_name: Optional[str] = None
    last_parameters: CaseParameters
    calculated_results: Optional[CaseResults] = None

class UserCaseInDB(UserCaseBase):
    id: int
    user_id: int
    session_token: Optional[str] = None
    last_activity_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True