# Calcul des métriques + backtest par CAGR

# Chemin d'accès:
# backend/app/calc.py

from datetime import datetime
from typing import Dict, List
import numpy as np
import pandas as pd

from .schemas import BacktestRequest, Metrics
from . import data_fetcher


def _cagr(series: pd.Series) -> float:
    """
    Calculates the CAGR = Compound Annual Growth Rate from a price series.
    CAGR = (Final_value / Initial_value)^(1/number_of_years) - 1
    """
    series = series.dropna() 
    if len(series) < 2:
        return 0.0
    start = series.iloc[0]
    end = series.iloc[-1]
    days = (series.index[-1] - series.index[0]).days
    if days <= 0:
        return 0.0
    years = days / 365.25
    return (end / start) ** (1 / years) - 1


def _vol(series: pd.Series) -> float:
    """
    Calculates annualized volatility from daily returns.
    252 : number of stock market days in a year
    """
    series = series.dropna()
    if len(series) < 2:
        return 0.0
    returns = series.pct_change().dropna()
    return float(returns.std() * np.sqrt(252))


def _max_drawdown(series: pd.Series) -> float:
    """
    Calculates maximum drawdown: worst loss relative to historical peak.
    Max Drawdown = min((Price - Peak)/Peak) 
    """
    series = series.dropna()
    if len(series) < 2:
        return 0.0
    peak = series.cummax() # cummax(): All-time high at each point
    dd = (series - peak) / peak
    return float(dd.min())

def _annualized_return(series: pd.Series) -> float:
    """
    Calculates simple annualized return (average yearly return).
    Different from CAGR: this is the arithmetic mean of annual returns.
    """
    series = series.dropna()
    if len(series) < 2:
        return 0.0
    returns = series.pct_change().dropna()
    days = len(returns)
    if days == 0:
        return 0.0
    # Annualize the mean daily return
    return float(returns.mean() * 252)


def _best_year(series: pd.Series) -> float:
    """
    Calculates the best annual return (highest yearly performance).
    """
    series = series.dropna()
    if len(series) < 2:
        return 0.0
    
    if not isinstance(series.index, pd.DatetimeIndex):
        try:
            series.index = pd.to_datetime(series.index)
        except Exception:
            return 0.0
    
    # Group by year and calculate annual returns
    yearly_returns = series.resample('YE').last().pct_change().dropna()
    
    if len(yearly_returns) == 0:
        return 0.0
    
    return float(yearly_returns.max())

def _worst_year(series: pd.Series) -> float:
    """
    Calculates the worst annual return (lowest yearly performance).
    """
    series = series.dropna()
    if len(series) < 2:
        return 0.0
    
    if not isinstance(series.index, pd.DatetimeIndex):
        try:
            series.index = pd.to_datetime(series.index)
        except Exception:
            return 0.0
    
    # Group by year and calculate annual returns
    yearly_returns = series.resample('YE').last().pct_change().dropna()
    
    if len(yearly_returns) == 0:
        return 0.0
    
    return float(yearly_returns.min())



def _sharpe_ratio(series: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculates the Sharpe Ratio: (Return - Risk_Free_Rate) / Volatility
    Default risk-free rate: 2% per year
    """
    series = series.dropna()
    if len(series) < 2:
        return 0.0
    
    returns = series.pct_change().dropna()
    if len(returns) == 0:
        return 0.0
    
    # Annualized return and volatility
    annual_return = returns.mean() * 252
    annual_vol = returns.std() * np.sqrt(252)
    
    if annual_vol == 0:
        return 0.0
    
    return float((annual_return - risk_free_rate) / annual_vol)

def compute_metrics(prices: pd.DataFrame) -> Dict[str, Metrics]:
    """
    Computes financial metrics (CAGR, volatility, max drawdown) 
    for each asset (column) in the DataFrame.
    """
    metrics: Dict[str, Metrics] = {}
    for col in prices.columns:
        s = prices[col]
        metrics[col] = Metrics(
            cagr=_cagr(s),
            vol=_vol(s),
            max_drawdown=_max_drawdown(s),
            annualized_return=_annualized_return(s),
            best_year=_best_year(s),
            worst_year=_worst_year(s),
            sharpe_ratio=_sharpe_ratio(s),
        )
    return metrics


def _build_portfolio_series_from_cagr(
    dates: pd.DatetimeIndex,
    assets: List[str],
    metrics: Dict[str, Metrics],
    invest_amount: float,
    weights: List[float],
    strategy: str,
) -> pd.Series:
    """
    Builds a synthetic portfolio time series using CAGR-based growth simulation.
    Supports two strategies:
    - buy_and_hold: Invest full amount at start
    - dca: Dollar-Cost Averaging with monthly contributions
    """

    weights_array = np.array(weights, dtype=float)
    weights_array = weights_array / weights_array.sum()  # Normalize weights to sum to 1

    # Convert annual CAGR to daily growth rate for each asset
    daily_rates = []
    for asset in assets:
        r_annual = metrics[asset].cagr
        daily = (1.0 + r_annual) ** (1.0 / 252.0) - 1.0
        daily_rates.append(daily)
    daily_rates = np.array(daily_rates)

    # Building the date series (calendar days)
    n_days = len(dates)
    days_index = np.arange(n_days, dtype=float)  # 0,1,2,... for exponentiation

    if strategy == "buy_and_hold":
        # Fully invested from the beginning 
        alloc_per_asset = invest_amount * weights_array
        # valeur(t) = alloc * (1 + r_daily)^t
        growth_factors = (1.0 + daily_rates) ** days_index[:, None]  # shape (n_days, n_assets)
        values = growth_factors * alloc_per_asset  # broadcast
        portfolio = values.sum(axis=1)  # sum over assets
        return pd.Series(portfolio, index=dates)

    elif strategy == "dca":
        # We invest the same amount at the beginning of each month.
        # Number of months in the investment period
        months = sorted(
            { (d.year, d.month) for d in dates }
        )
        if not months:
            return pd.Series([0.0] * n_days, index=dates)

        n_months = len(months)
        monthly_contrib_total = invest_amount / n_months

        # mapping (year, month) -> index in dates
        first_day_idx_per_month = {}
        for idx, d in enumerate(dates):
            key = (d.year, d.month)
            if key not in first_day_idx_per_month:
                first_day_idx_per_month[key] = idx

        # Building the portfolio value day by day
        portfolio = np.zeros(n_days, dtype=float)

        for key in months:
            start_idx = first_day_idx_per_month[key]
            # This month, we invest a total amount
            alloc_per_asset = monthly_contrib_total * weights_array
            # days from start_idx
            local_days = np.arange(n_days - start_idx, dtype=float)
            growth = (1.0 + daily_rates) ** local_days[:, None]
            contrib_values = growth * alloc_per_asset
            portfolio[start_idx:] += contrib_values.sum(axis=1)

        return pd.Series(portfolio, index=dates)

    else:
        # if unknown strategy
        return pd.Series([0.0] * n_days, index=dates)


def run_backtest(req: BacktestRequest):
    """
    Executes a complete backtest workflow:
    1. Fetches historical prices for the assets
    2. Computes performance metrics (CAGR, volatility, drawdown)
    3. Simulates portfolio growth using CAGR-based projections
    """

    # Some basic validations.
    TOLERANCE = 1e-6 # Point-float tolerance for weight sum check.
    if not np.isclose(sum(req.weights), 1.0, atol=TOLERANCE):
        raise ValueError("Weight sum must be 1.")
 
    if len(req.assets) != len(req.weights):
        raise ValueError("Number of assets does not match number of weights.")
    

    # 1. Fetch price data for metrics calculation
    prices = data_fetcher.get_prices(
        req.assets,
        start_date=str(req.start_date),
        end_date=str(req.end_date),
    )
    if prices.empty:
        raise ValueError("No price data for the requested assets.")
    
    # If the calculation requires at least two data points (start and end), check for that.
    if prices.empty or len(prices) < 2:
        
        # Define the REQUIRED nested structure with default safe values
        safe_metrics = {
            "portfolio": {
                "cagr": 0.0,
                "vol": 0.0,
                "max_drawdown": 0.0
            }
        }
        # Return an empty portfolio series and the structured metrics
        return pd.Series(), safe_metrics
    
    # 2. Calculate performance metrics
    metrics = compute_metrics(prices)

    # 3. Build synthetic portfolio series over strategy period
    strat_dates = pd.date_range(
        start=req.strat_start,
        end=req.strat_end,
        freq="D",
    )
    portfolio_series = _build_portfolio_series_from_cagr(
        dates=strat_dates,
        assets=req.assets,
        metrics=metrics,
        invest_amount=req.invest_amount,
        weights=req.weights,
        strategy=req.strategy,
    )
    
    
    return portfolio_series, metrics
