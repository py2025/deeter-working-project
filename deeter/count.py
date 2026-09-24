"""Counting pass: names per week over the sample, with no outcome data loaded.

Checks the "a few names" target (3-10 a week) and the rule frequencies DEFINITIONS.md assumes.
Usage: python -m deeter.count
"""

from pathlib import Path

import pandas as pd

from deeter.config import Config
from deeter.data import load_prices
from deeter.rules import find_setups, in_universe, market_model, weeks

OUTPUT = Path(__file__).resolve().parent.parent / "output"


def sample_weeks(index: pd.DatetimeIndex, cfg: Config) -> pd.Series:
    """Weeks where every possible ignition day has a full volatility window."""
    w = weeks(index)
    return w[w.index >= index[cfg.vol_window + cfg.consol_max + 1]]


def main() -> None:
    cfg = Config()
    p = load_prices()
    w = sample_weeks(p["close"].index, cfg)
    print(f"{len(w)} weeks: screen dates {w.index[0].date()} to {w.index[-1].date()}")

    universe = in_universe(p, cfg)
    print(f"Universe size on screen dates: median {universe.loc[w.index].sum(axis=1).median():.0f}")

    # How often each ignition rule fires, per stock-day in the universe (section 2-3 claims)
    e, _, sigma = market_model(p, cfg)
    volume = p["volume"]
    base_volume = volume.rolling(cfg.volume_window).median().shift(1)
    days = universe.loc[w.index[0]:].to_numpy()
    share = lambda rule: rule.loc[w.index[0]:].to_numpy()[days].mean()
    big_move = share(e.abs() >= cfg.ignition_sigma * sigma)
    heavy = share(volume >= cfg.volume_mult * base_volume)
    print(f"Share of stock-days: move >= {cfg.ignition_sigma} sigma {big_move:.1%}, "
          f"volume >= {cfg.volume_mult}x {heavy:.1%}")

    setups = find_setups(p, cfg, w.index)
    per_week = (setups.pivot_table(index="date", columns="direction", values="ticker", aggfunc="count")
                .reindex(w.index, fill_value=0).fillna(0).astype(int)
                .rename(columns={1.0: "up", -1.0: "down"}))
    per_week["total"] = per_week.sum(axis=1)
    per_week.to_csv(OUTPUT / "counts_per_week.csv")

    print("\nSetups per week")
    print(per_week.describe(percentiles=[0.25, 0.5, 0.75]).loc[["mean", "min", "25%", "50%", "75%", "max"]].round(1))
    print(f"Weeks with no setups: {(per_week['total'] == 0).sum()} of {len(per_week)}")


if __name__ == "__main__":
    main()
