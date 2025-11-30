# — récupération des prix (Yahoo Finance)
# Indispensable, il télécharge les données via Yahoo Finance (yfinance)
# Il les stocke en CSV ou dans SQLite
# Il est appelé par le backend pour pouvoir backtester

# Chemin d'accès:
# backend/app/data_fetcher.py

import yfinance as yf
import pandas as pd
from typing import List
#from .db import engine


def get_prices(
    symbols: List[str],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Récupère les prix de clôture ajustés pour une liste de symboles
    entre start_date et end_date (format 'YYYY-MM-DD').

    Retourne un DataFrame indexé par date, colonnes = symboles.
    """
    if not symbols:
        return pd.DataFrame()

    data = yf.download(
        tickers=symbols,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )

    # Si plusieurs tickers, yfinance renvoie un MultiIndex de colonnes
    if isinstance(data.columns, pd.MultiIndex):
        close = data["Close"]
    else:
        # Un seul ticker
        close = data[["Close"]]
        close.columns = [symbols[0]]

    # On fait .dropna() pour enlever les dates sans données
    close = close.dropna()

    # TODO: Stocker dans SQLite.

    return close
