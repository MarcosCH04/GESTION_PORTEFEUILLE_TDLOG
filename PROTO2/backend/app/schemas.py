from typing import List, Dict, Literal, Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

# --- 1. Core Metrics ---
class Metrics(BaseModel):
    cagr: float
    vol: float
    max_drawdown: float

# --- 2. API Request/Response Schemas ---
class AnalyzeRequest(BaseModel):
    assets: List[str]
    start_date: date
    end_date: date

class AnalyzeResponse(BaseModel):
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
    portfolio: Dict[str, float]
    metrics: Dict[str, Metrics]

# --- 3. Strategy Storage Schemas ---

class UserStrategySchema(BaseModel):
    """Schema for the UserStrategy table records."""
    id: int
    name: str
    parameters: BacktestRequest # The inputs used for the backtest
    is_saved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- 4. Database/Auth Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    # Optional allows it to be None/Missing without crashing the API response
    created_at: Optional[datetime] = None 
    strategies: List[UserStrategySchema] = [] 

    model_config = ConfigDict(from_attributes=True)