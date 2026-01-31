from typing import List, Dict, Literal, Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

# --- 1. Core Metrics ---
class Metrics(BaseModel):
    # Key performance metrics for investment analysis and backtesting
    cagr: float
    vol: float
    max_drawdown: float
    annualized_return: float = 0.0 
    best_year: float = 0.0           
    worst_year: float = 0.0          
    sharpe_ratio: float = 0.0
# --- 2. API Request/Response Schemas ---
class AnalyzeRequest(BaseModel):
    # List of asset tickers and date range for analysis
    assets: List[str]
    start_date: date
    end_date: date

class AnalyzeResponse(BaseModel):
    # Asset prices and computed metrics for each asset
    prices: Dict[str, Dict[str, float]] 
    metrics: Dict[str, Metrics]

class BacktestRequest(BaseModel):
    # Parameters for running an investment strategy backtest
    assets: List[str]
    start_date: date
    end_date: date
    invest_amount: float
    weights: List[float]
    strategy: Literal["buy_and_hold", "dca"]
    strat_start: date
    strat_end: date

class BacktestResponse(BaseModel):
    # Results of the backtest including portfolio values and metrics
    portfolio: Dict[str, float]
    metrics: Dict[str, Metrics]
    asset_prices: Dict[str, Dict[str, float]]

# --- 3. Strategy Storage Schemas ---

class UserStrategySchema(BaseModel):
    # Schema for user-saved investment strategies in the database
    id: int
    name: str
    parameters: BacktestRequest # The inputs used for the backtest
    is_saved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SaveRequest(BaseModel):
    # Schema for extra data needed to save a user strategy
    name: str

# --- 4. Database/Auth Schemas ---
class UserBase(BaseModel):
    # Basic user information
    username: str

class UserCreate(UserBase):
    # User creation schema with password
    password: str

class UserInDB(UserBase):
    # User schema as stored in the database
    id: int
    # Optional allows it to be None/Missing without crashing the API response
    created_at: Optional[datetime] = None 
    strategies: List[UserStrategySchema] = [] 

    model_config = ConfigDict(from_attributes=True)