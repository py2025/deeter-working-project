"""Sensitivity grid declared in DEFINITIONS.md: 27 threshold combinations, all reported.

The headline result stays the default settings, whatever the grid shows.
Usage: python -m deeter.grid
"""

from dataclasses import replace
from itertools import product
from pathlib import Path

import pandas as pd

from deeter.backtest import backtest, base_rates, show, summarize
from deeter.config import Config
from deeter.count import sample_weeks
from deeter.data import load_prices
from deeter.rules import market_model

OUTPUT = Path(__file__).resolve().parent.parent / "output"
GRID = {
    "ignition_sigma": [2.0, 2.5, 3.0],
    "volume_mult": [2.0, 3.0, 4.0],
    "min_hold": [0.33, 0.5, 0.67],
}


def main() -> None:
    cfg = Config()
    p = load_prices()
    w = sample_weeks(p["close"].index, cfg)
    base = base_rates(p, cfg, w)  # none of the grid thresholds affect these two
    model = market_model(p, cfg)

    rows = {}
    for values in product(*GRID.values()):
        settings = dict(zip(GRID, values))
        label = "  ".join(f"{name}={value}" for name, value in settings.items())
        if replace(cfg, **settings) == cfg:
            label += "  (default)"
        rows[label] = summarize(backtest(p, replace(cfg, **settings), w, base, model=model))
        print(f"done: {label}", flush=True)

    table = pd.DataFrame(rows).T
    table.insert(2, "per_week", table["setups"] / len(w))
    table.to_csv(OUTPUT / "grid.csv")
    columns = ["setups", "per_week", "goes_again", "reverses", "edge", "edge_lo", "edge_hi", "oc_mean_bps"]
    print("\nPercentages, except setups, per_week and oc_mean_bps. Ranges are 90%, resampling weeks.\n")
    print(show(table[columns]))


if __name__ == "__main__":
    main()
