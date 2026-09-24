"""Friday outcomes (DEFINITIONS.md section 5). The only module that reads data after the screen date."""

import numpy as np
import pandas as pd


def add_outcomes(setups: pd.DataFrame, p: dict, weeks: pd.Series) -> pd.DataFrame:
    """Label each setup's outcome day D. `weeks` maps screen date S -> D.

    Returns are in the direction of the setup (positive = the move continued) and use the beta
    known at the screen date.
    """
    df = setups.copy()
    close = p["close"]
    i = close.index.get_indexer(weeks.loc[df["date"]])
    j = close.columns.get_indexer(df["ticker"])
    s = close.index.get_indexer(df["date"])
    close_d, open_d = close.to_numpy()[i, j], p["open"].to_numpy()[i, j]
    spy_open_to_close = close["SPY"].to_numpy()[i] / p["open"]["SPY"].to_numpy()[i] - 1
    spy_close_to_close = close["SPY"].to_numpy()[i] / close["SPY"].to_numpy()[s] - 1

    d = df["direction"].to_numpy()
    beyond = np.where(d > 0, close_d > df["range_hi"], close_d < df["range_lo"])
    against = np.where(d > 0, close_d < df["range_lo"], close_d > df["range_hi"])
    df["outcome"] = np.select([np.isnan(close_d), beyond, against],
                              ["missing", "goes again", "reverses"], "stalls")
    df["open_to_close"] = d * ((close_d / open_d - 1) - df["beta"] * spy_open_to_close)
    df["close_to_close"] = d * ((close_d / df["close"] - 1) - df["beta"] * spy_close_to_close)
    df["gap"] = d * (open_d / df["close"] - 1)
    return df
