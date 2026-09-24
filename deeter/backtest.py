"""Backtest over recent weeks (DEFINITIONS.md, Evidence protocol).

Runs the screen on every historical screen date, labels the following outcome day, and compares
the setups with (1) every universe stock on the same day and (2) ignitions that didn't consolidate.
Usage: python -m deeter.backtest
"""

from pathlib import Path

import numpy as np
import pandas as pd

from deeter.config import Config
from deeter.count import sample_weeks
from deeter.data import load_prices
from deeter.outcomes import add_outcomes
from deeter.rules import LEANS, find_setups, in_universe

OUTPUT = Path(__file__).resolve().parent.parent / "output"


def close_third(close_loc):
    """Which third of its range the screen-date close sat in: 0 bottom, 1 middle, 2 top."""
    return np.floor(close_loc * 3).clip(0, 2).fillna(1)


def base_rates(p: dict, cfg: Config, w: pd.Series) -> pd.DataFrame:
    """How often an ordinary universe stock's outcome-day close breaks above / below its own
    k-day range, per screen date, k and close third. The benchmark for "goes again" and "reverses".

    Matching on the close third matters: a stock that closes near the top of its range needs only
    a small move to break above it, setup or not. The *_all columns ignore the close third.
    """
    universe = in_universe(p, cfg).loc[w.index]
    close_s = p["close"].loc[w.index]
    close_d = p["close"].loc[w.to_numpy()].set_axis(w.index)
    rows = []
    for k in range(cfg.consol_min, cfg.consol_max + 1):
        hi = p["high"].rolling(k).max().loc[w.index]
        lo = p["low"].rolling(k).min().loc[w.index]
        stocks = pd.DataFrame({
            "third": close_third((close_s - lo) / (hi - lo)).stack(future_stack=True),
            "base_up": (close_d > hi).stack(future_stack=True),
            "base_down": (close_d < lo).stack(future_stack=True),
            "in_universe": universe.stack(future_stack=True),
        })
        stocks = stocks[stocks["in_universe"]].reset_index()
        matched = stocks.groupby(["date", "third"])[["base_up", "base_down"]].mean()
        overall = stocks.groupby("date")[["base_up", "base_down"]].mean().add_suffix("_all")
        rows.append(matched.reset_index().merge(overall, on="date").assign(consol_days=k))
    return pd.concat(rows)


def backtest(p: dict, cfg: Config, w: pd.Series, base: pd.DataFrame,
             consolidated: bool = True) -> pd.DataFrame:
    """Setups on every screen date in `w`, with outcomes and the matching base rates."""
    df = find_setups(p, cfg, w.index, consolidated)
    if not consolidated:  # a stock can fail more than once a week; keep its latest ignition
        df = df.sort_values("consol_days").drop_duplicates(["date", "ticker"])
    df = add_outcomes(df, p, w)
    df = df.assign(third=close_third(df["close_loc"])).merge(base, on=["date", "consol_days", "third"])
    up = df["direction"] > 0
    for suffix in ["", "_all"]:
        df["base_go" + suffix] = np.where(up, df["base_up" + suffix], df["base_down" + suffix])
        df["base_rev" + suffix] = np.where(up, df["base_down" + suffix], df["base_up" + suffix])
    return df[df["outcome"] != "missing"]


def interval(num: np.ndarray, den: np.ndarray, n: int = 5000, seed: int = 0) -> np.ndarray:
    """90% range of sum(num) / sum(den) when whole weeks are resampled with replacement."""
    idx = np.random.default_rng(seed).integers(len(num), size=(n, len(num)))
    return np.percentile(num[idx].sum(axis=1) / den[idx].sum(axis=1), [5, 95])


def summarize(df: pd.DataFrame) -> dict:
    """One row of evidence for a group of setups.

    edge = (goes again - reverses) for the setups, minus the same difference for ordinary stocks
    on that day in the same close third. Narrow ranges make both breaks more likely, so the
    difference is the fair test, not the goes-again rate alone. edge_range_only skips the
    close-third matching (shown to make the close-location artifact visible).
    """
    df = df.assign(n=1, go=df["outcome"] == "goes again", stall=df["outcome"] == "stalls",
                   rev=df["outcome"] == "reverses")
    go_minus_rev = df["go"].astype(int) - df["rev"].astype(int)
    df["edge"] = go_minus_rev - (df["base_go"] - df["base_rev"])
    df["edge_all"] = go_minus_rev - (df["base_go_all"] - df["base_rev_all"])
    cols = ["n", "go", "stall", "rev", "base_go", "base_rev", "edge", "edge_all", "open_to_close"]
    weekly = df.groupby("date")[cols].sum()
    n = weekly["n"].to_numpy()
    rate = lambda col: weekly[col].sum() / n.sum()
    edge_range = interval(weekly["edge"].to_numpy(), n)
    oc_range = interval(weekly["open_to_close"].to_numpy(), n) * 1e4
    return {
        "setups": int(n.sum()), "weeks": len(weekly),
        "goes_again": rate("go"), "stalls": rate("stall"), "reverses": rate("rev"),
        "base_goes": rate("base_go"), "base_reverses": rate("base_rev"),
        "edge": rate("edge"), "edge_lo": edge_range[0], "edge_hi": edge_range[1],
        "edge_range_only": rate("edge_all"),
        "oc_mean_bps": rate("open_to_close") * 1e4, "oc_lo_bps": oc_range[0], "oc_hi_bps": oc_range[1],
        "oc_median_bps": df["open_to_close"].median() * 1e4,
        "oc_positive": (df["open_to_close"] > 0).mean(),
    }


def show(table: pd.DataFrame) -> str:
    """Percentages and basis points, rounded for reading."""
    t = table.copy()
    pct = ["goes_again", "stalls", "reverses", "base_goes", "base_reverses", "edge", "edge_lo",
           "edge_hi", "edge_range_only", "oc_positive"]
    t[pct] = t[pct].astype(float) * 100
    return t.astype(float).round(1).to_string()


def main() -> None:
    cfg = Config()
    p = load_prices()
    w = sample_weeks(p["close"].index, cfg)
    base = base_rates(p, cfg, w)
    df = backtest(p, cfg, w, base)
    df.to_csv(OUTPUT / "backtest_setups.csv", index=False)

    busiest = df.groupby("date").size().nlargest(5)
    half = w.index[len(w) // 2]
    groups = {
        "All setups": df,
        "Up-moves": df[df["direction"] > 0],
        "Down-moves": df[df["direction"] < 0],
        **{f"Lean: {lean}": df[df["lean"] == lean] for lean in LEANS.values()},
        "First half": df[df["date"] < half],
        "Second half": df[df["date"] >= half],
        "Without the 5 busiest weeks": df[~df["date"].isin(busiest.index)],
        "Ignitions that didn't consolidate": backtest(p, cfg, w, base, consolidated=False),
    }
    table = pd.DataFrame({name: summarize(g) for name, g in groups.items()}).T
    table.to_csv(OUTPUT / "backtest_summary.csv")
    print("Percentages, except setups, weeks and *_bps (basis points). Ranges are 90%, resampling weeks.\n")
    print(show(table))

    spy = p["close"]["SPY"]
    print("\nBusiest weeks")
    for date, count in busiest.items():
        outcomes = df.loc[df["date"] == date, "outcome"].value_counts().to_dict()
        spy_week = spy.loc[:date].iloc[-1] / spy.loc[:date].iloc[-6] - 1
        print(f"{date.date()}  {count} setups  SPY over the prior 5 sessions {spy_week:+.1%}  {outcomes}")


if __name__ == "__main__":
    main()
