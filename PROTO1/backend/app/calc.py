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
    Calcule le CAGR (taux de croissance annualisé) à partir d'une série de prix.
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
    Volatilité annualisée à partir des rendements journaliers.
    """
    series = series.dropna()
    if len(series) < 2:
        return 0.0
    returns = series.pct_change().dropna()
    return float(returns.std() * np.sqrt(252))


def _max_drawdown(series: pd.Series) -> float:
    """
    Max drawdown : pire perte relative par rapport au plus haut historique.
    """
    series = series.dropna()
    if len(series) < 2:
        return 0.0
    peak = series.cummax()
    dd = (series - peak) / peak
    return float(dd.min())


def compute_metrics(prices: pd.DataFrame) -> Dict[str, Metrics]:
    """
    Calcule les métriques pour chaque colonne (ticker) du DataFrame.
    """
    metrics: Dict[str, Metrics] = {}
    for col in prices.columns:
        s = prices[col]
        metrics[col] = Metrics(
            cagr=_cagr(s),
            vol=_vol(s),
            max_drawdown=_max_drawdown(s),
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
    Construit une série temporelle de valeur de portefeuille en utilisant
    uniquement les CAGR de chaque actif.

    - buy_and_hold : on investit tout au début.
    - dca         : on investit une somme fixe au début de chaque mois.
    """
    weights = np.array(weights, dtype=float)
    weights = weights / weights.sum()  # normalisation

    # Pour chaque actif, on calcule un taux de croissance quotidien
    # à partir du CAGR annuel.
    daily_rates = []
    for asset in assets:
        r_annual = metrics[asset].cagr
        # croissance composée quotidienne approx.
        daily = (1.0 + r_annual) ** (1.0 / 252.0) - 1.0
        daily_rates.append(daily)
    daily_rates = np.array(daily_rates)

    # Construction de la série de dates (jours calendaires)
    n_days = len(dates)
    days_index = np.arange(n_days, dtype=float)  # 0,1,2,... pour l'exponentiation

    if strategy == "buy_and_hold":
        # Tout investi au début
        alloc_per_asset = invest_amount * weights
        # valeur(t) = alloc * (1 + r_daily)^t
        growth_factors = (1.0 + daily_rates) ** days_index[:, None]  # shape (n_days, n_assets)
        values = growth_factors * alloc_per_asset  # broadcast
        portfolio = values.sum(axis=1)  # somme sur les actifs
        return pd.Series(portfolio, index=dates)

    elif strategy == "dca":
        # On investit la même somme au début de chaque mois.
        # Nombre de mois dans la période
        months = sorted(
            { (d.year, d.month) for d in dates }
        )
        if not months:
            return pd.Series([0.0] * n_days, index=dates)

        n_months = len(months)
        monthly_contrib_total = invest_amount / n_months

        # mapping (year, month) -> index dans dates
        first_day_idx_per_month = {}
        for idx, d in enumerate(dates):
            key = (d.year, d.month)
            if key not in first_day_idx_per_month:
                first_day_idx_per_month[key] = idx

        # on construit la valeur de portefeuille jour par jour
        portfolio = np.zeros(n_days, dtype=float)

        for key in months:
            start_idx = first_day_idx_per_month[key]
            # ce mois-là, on investit une somme totale
            alloc_per_asset = monthly_contrib_total * weights
            # les jours à partir de start_idx
            local_days = np.arange(n_days - start_idx, dtype=float)
            growth = (1.0 + daily_rates) ** local_days[:, None]
            contrib_values = growth * alloc_per_asset
            portfolio[start_idx:] += contrib_values.sum(axis=1)

        return pd.Series(portfolio, index=dates)

    else:
        # Au cas où, on ne fait rien de spécial
        return pd.Series([0.0] * n_days, index=dates)


def run_backtest(req: BacktestRequest):
    """
    Backtest global :
    1. Récupère les prix des actifs sur la période de backtest (start_date, end_date).
    2. Calcule les métriques (CAGR, vol, max drawdown).
    3. Construit un portefeuille synthétique sur [strat_start, strat_end]
       en utilisant les CAGR uniquement.
    """
    # 1. Prix pour le calcul des métriques
    prices = data_fetcher.get_prices(
        req.assets,
        start_date=str(req.start_date),
        end_date=str(req.end_date),
    )
    if prices.empty:
        raise ValueError("Pas de données de prix pour les actifs demandés.")

    # 2. Métriques
    metrics = compute_metrics(prices)

    # 3. Série temporelle synthétique de portefeuille
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
