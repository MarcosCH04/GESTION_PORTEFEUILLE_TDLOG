# backend/app/schemas.py

from typing import List, Dict, Literal, Optional
from datetime import date, datetime
from pydantic import BaseModel

# --- Core Metrics ---
class Metrics(BaseModel):
    cagr: float
    vol: float
    max_drawdown: float

# --- API Request/Response Schemas ---
class AnalyzeRequest(BaseModel):
    assets: List[str]
    start_date: date
    end_date: date

class AnalyzeResponse(BaseModel):
    # Prices returned as {date_str: {symbol: price}}
    prices: Dict[str, Dict[str, float]] 
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
    portfolio: Dict[str, float] # {date_str: portfolio_value}
    metrics: Dict[str, Metrics]

# --- Database/Auth Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class CaseParameters(BacktestRequest):
    """Schema for storing request body in UserCase.last_parameters."""
    pass

class CaseResults(BaseModel):
    """Schema for storing response body in UserCase.calculated_results."""
    portfolio: Dict[str, float]
    metrics: Dict[str, Metrics]