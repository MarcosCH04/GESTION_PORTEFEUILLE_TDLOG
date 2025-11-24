# — récupération des prix (Yahoo Finance)
# Indispensable, il télécharge les données via Yahoo Finance (yfinance)
# Il les stocke en CSV ou dans SQLite
# Il est appelé par le backend pour pouvoir backtester

# Chemin d'accès:
# backend/app/data_fetcher.py

import yfinance as yf
import pandas as pd
from typing import List
from .db import engine


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

    close = close.dropna()

    # (Option pédagogique) : montrer comment on pourrait stocker en base SQLite
    # Ici, on crée une table prices_raw, écrasée à chaque appel (demo simple).
    try:
        df_to_store = close.copy()
        df_to_store.reset_index(inplace=True)
        df_to_store.to_sql(
            "prices_raw",
            con=engine,
            if_exists="replace",
            index=False,
        )
    except Exception:
        # Si problème d'écriture, on ignore (ce n'est pas bloquant pour le projet).
        pass

    return close
