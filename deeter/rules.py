"""Setup rules: universe, ignition, volume, consolidation, lean (DEFINITIONS.md sections 1-4, 6).

Everything here uses rolling windows and backward shifts only, so a setup on screen date S
is built from data up to S's close and nothing later.
"""

import numpy as np
import pandas as pd

from deeter.config import Config

LEANS = {3: "Goes", 2: "Leans goes", 1: "Leans stalls", 0: "Stalls"}


def weeks(index: pd.DatetimeIndex) -> pd.Series:
    """Screen date S -> outcome date D for each complete calendar week (D = last session)."""
    outcome = pd.Series(index, index=index).groupby(index.to_period("W")).max()
    if index[-1].weekday() != 4:  # the latest week is still running
        outcome = outcome.iloc[:-1]
    pos = index.get_indexer(outcome)
    return pd.Series(index[pos], index=index[pos - 1])


def market_model(p: dict, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Excess return e, beta and residual volatility sigma for every stock-day.

    beta and sigma come from the vol_window sessions ending the day before.
    """
    r = p["close"].pct_change(fill_method=None)
    m = r["SPY"]
    cov = r.rolling(cfg.vol_window).cov(m)
    var_m = m.rolling(cfg.vol_window).var()
    beta = (cov.div(var_m, axis=0)).shift(1)
    resid_var = r.rolling(cfg.vol_window).var() - cov.pow(2).div(var_m, axis=0)  # OLS identity
    sigma = np.sqrt(resid_var.clip(lower=0)).shift(1)
    e = r - beta.mul(m, axis=0)
    return e, beta, sigma


def in_universe(p: dict, cfg: Config) -> pd.DataFrame:
    """Section 1: price and liquidity, measured on the session before."""
    close = p["close"]
    dollar_volume = (close * p["volume"]).rolling(cfg.dollar_volume_window).median().shift(1)
    return (close.shift(1) > cfg.min_price) & (dollar_volume >= cfg.min_dollar_volume)


def ignitions(p: dict, e: pd.DataFrame, sigma: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Sections 1-3: in the universe, an unusual excess move, and heavy volume."""
    close, volume = p["close"], p["volume"]
    big_move = e.abs() >= cfg.ignition_sigma * sigma
    same_way = np.sign(e) == np.sign(close.pct_change(fill_method=None))  # raw move agrees
    heavy = volume >= cfg.volume_mult * volume.rolling(cfg.volume_window).median().shift(1)
    return in_universe(p, cfg) & big_move & same_way & heavy


def find_setups(p: dict, cfg: Config, dates, consolidated: bool = True) -> pd.DataFrame:
    """Every setup whose screen date S is in `dates`: one row per stock, with the numbers
    behind each rule and the lean.

    consolidated=False instead returns ignitions that failed the consolidation rules (the
    backtest's comparison group).
    """
    e, beta, sigma = market_model(p, cfg)
    ignited = ignitions(p, e, sigma, cfg)
    close, volume = p["close"], p["volume"]
    base_volume = volume.rolling(cfg.volume_window).median().shift(1)

    rows = []
    for k in range(cfg.consol_min, cfg.consol_max + 1):  # k consolidation days, I = S - k
        sigma_i = sigma.shift(k)
        hold = (close - close.shift(k + 1)) / (close.shift(k) - close.shift(k + 1))
        consolidates = (e.abs().rolling(k).max() < cfg.consol_sigma * sigma_i) & (hold >= cfg.min_hold)
        setup = ignited.shift(k, fill_value=False) & (consolidates if consolidated else ~consolidates)
        range_hi = p["high"].rolling(k).max()
        range_lo = p["low"].rolling(k).min()
        numbers = {
            "direction": np.sign(e.shift(k)),
            "ignition_sigma": (e / sigma).shift(k),
            "rel_volume": (volume / base_volume).shift(k),
            "max_quiet_sigma": e.abs().rolling(k).max() / sigma_i,
            "hold": hold,
            "range_lo": range_lo,
            "range_hi": range_hi,
            "close": close,
            "close_loc": (close - range_lo) / (range_hi - range_lo),
            "volume_ratio": volume.rolling(k).mean() / volume.shift(k),
            "consol_excess": e.rolling(k).sum(),
            "beta": beta,
        }
        hits = setup.loc[dates].stack()
        hits = hits[hits].index
        i = close.index.get_indexer(hits.get_level_values(0))
        j = close.columns.get_indexer(hits.get_level_values(1))
        df = pd.DataFrame({name: f.to_numpy()[i, j] for name, f in numbers.items()}, index=hits)
        df["consol_days"] = k
        rows.append(df)

    df = pd.concat(rows).rename_axis(["date", "ticker"]).reset_index()
    d = df["direction"]
    df["vote_close"] = np.where(d > 0, df["close_loc"] >= cfg.lean_close_loc,
                                df["close_loc"] <= 1 - cfg.lean_close_loc)
    df["vote_volume"] = df["volume_ratio"] <= cfg.lean_volume_ratio
    df["vote_strength"] = d * df["consol_excess"] > 0
    df["votes"] = df[["vote_close", "vote_volume", "vote_strength"]].sum(axis=1)
    df["lean"] = df["votes"].map(LEANS)
    return df.sort_values(["date", "votes"], ascending=[True, False]).reset_index(drop=True)
