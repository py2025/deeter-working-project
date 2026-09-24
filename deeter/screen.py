"""Thursday-night list as of the latest close, or as of a past date.

Usage: python -m deeter.screen [YYYY-MM-DD]
"""

import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write image files; no window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

from deeter.config import Config
from deeter.data import load_prices
from deeter.rules import find_setups

OUTPUT = Path(__file__).resolve().parent.parent / "output"
# Chart colors: light surface, ink for all text, one accent for price
SURFACE, INK, INK_2, MUTED, GRID, ACCENT = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#2a78d6"
VOTES = {  # (for, against), phrased for the direction of the move
    "vote_close": ("closed at the {end} of its range", "closed away from the {end} of its range"),
    "vote_volume": ("volume dried up", "volume stayed heavy"),
    "vote_strength": ("{went} SPY", "{against} SPY"),
}


def reason(row: pd.Series) -> str:
    up = row["direction"] > 0
    words = {"end": "top" if up else "bottom", "went": "beat" if up else "lagged",
             "against": "lagged" if up else "beat"}
    way = "Up" if up else "Down"
    pro = [VOTES[v][0].format(**words) for v in VOTES if row[v]]
    con = [VOTES[v][1].format(**words) for v in VOTES if not row[v]]
    return (f"{way} {abs(row['ignition_sigma']):.1f} sigma on {row['rel_volume']:.1f}x volume, "
            f"{row['consol_days']} quiet days holding {row['hold']:.0%}. "
            f"For: {', '.join(pro) or 'nothing'}. Against: {', '.join(con) or 'nothing'}.")


def earnings_flag(ticker: str, start: pd.Timestamp, end: pd.Timestamp) -> str:
    """Section 7: does yfinance list an earnings date between the ignition and Friday?"""
    try:
        dates = yf.Ticker(ticker).get_earnings_dates(limit=12).index.tz_localize(None).normalize()
    except Exception:  # yfinance has no earnings data for many names
        return "unknown"
    return "yes" if ((dates >= start) & (dates <= end)).any() else "no"


def levels(row: pd.Series) -> str:
    """The Friday closes that decide the outcome (DEFINITIONS.md section 5)."""
    go, rev = ("above", "below") if row["direction"] > 0 else ("below", "above")
    go_at, rev_at = (row["range_hi"], row["range_lo"]) if row["direction"] > 0 else (row["range_lo"], row["range_hi"])
    return f"Friday: goes again on a close {go} {go_at:.2f}, reverses on a close {rev} {rev_at:.2f}."


def plot_screen(df: pd.DataFrame, close: pd.DataFrame, screen_date: pd.Timestamp, path: Path) -> None:
    """One small chart per name: the last 20 sessions, the ignition day, the quiet range carried
    into an empty Friday slot, the lean and the reason."""
    cols = 2
    rows = -(-len(df) // cols)  # round up
    height = 4.6 * rows + 0.8
    fig, axes = plt.subplots(rows, cols, figsize=(12, height), squeeze=False, facecolor=SURFACE)
    fig.text(0.01, 1 - 0.25 / height, f"Thursday screen  ·  {screen_date:%a %b %d, %Y} close  ·  "
             f"{len(df)} names", va="top", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.01, 1 - 0.6 / height, "Shaded band: the quiet range since the ignition. A Friday close "
             "beyond it in the direction of the move = goes again; inside = stalls.",
             va="top", fontsize=9, color=INK_2)
    for ax in axes.flat[len(df):]:
        ax.set_visible(False)

    for ax, (_, row) in zip(axes.flat, df.iterrows()):
        price = close[row["ticker"]].loc[:screen_date].iloc[-20:]
        x = np.arange(len(price))  # trading sessions, so weekends don't stretch the line
        thu, ign = x[-1], price.index.get_loc(row["ignition_date"])
        ax.set_facecolor(SURFACE)
        ax.fill_between([ign + 0.5, thu + 1.5], row["range_lo"], row["range_hi"], color=ACCENT,
                        alpha=0.12, lw=0)
        ax.plot(x, price, color=ACCENT, lw=2, solid_capstyle="round")
        ax.scatter([ign, thu], price.iloc[[ign, thu]], s=64, color=ACCENT, edgecolor=SURFACE,
                   linewidth=2, zorder=3)
        ax.annotate("ignition", (ign, price.iloc[ign]), xytext=(0, 9 * row["direction"]),
                    textcoords="offset points", ha="center", va="center", fontsize=8, color=INK_2)
        ax.annotate("Thu", (thu, price.iloc[thu]), xytext=(7, 0), textcoords="offset points",
                    va="center", fontsize=8, color=INK_2)

        ticks = list(range(thu % 5, thu, 5)) + [thu + 1]
        ax.set_xticks(ticks, [f"{price.index[t]:%b %d}" for t in ticks[:-1]] + ["Fri"])
        ax.set_xlim(-0.5, thu + 1.5)

        flag = "   ·   earnings" if row["earnings"] == "yes" else ""
        ax.set_title(f"{row['ticker']}   {row['lean']}{flag}", loc="left", fontsize=13,
                     fontweight="bold", color=INK)
        text = textwrap.fill(row["reason"], 78) + "\n" + textwrap.fill(levels(row), 78)
        ax.text(0, -0.16, text, transform=ax.transAxes, va="top", fontsize=9, color=INK_2)

        ax.grid(axis="y", color=GRID, lw=1)
        ax.set_axisbelow(True)
        ax.tick_params(colors=MUTED, labelsize=8, length=0)
        for side, spine in ax.spines.items():
            spine.set_visible(side == "bottom")
            spine.set_color(GRID)

    fig.subplots_adjust(left=0.05, right=0.98, top=1 - 1.3 / height, bottom=0.9 / height,
                        hspace=0.75, wspace=0.18)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    cfg = Config()
    p = load_prices()
    index = p["close"].index
    screen_date = pd.Timestamp(sys.argv[1]) if len(sys.argv) > 1 else index[-1]
    if screen_date not in index:
        sys.exit(f"{screen_date:%Y-%m-%d} is not a trading day in the downloaded data.")
    print(f"Screen as of the {screen_date:%A %Y-%m-%d} close")
    if screen_date.weekday() != 3:
        print("Note: not a Thursday. The list assumes the next session is the outcome day.")

    df = find_setups(p, cfg, [screen_date])
    if df.empty:
        print("0 names: no stock passed every rule this week.")
        return
    pos = index.get_loc(screen_date)
    df["ignition_date"] = [index[pos - k] for k in df["consol_days"]]
    # From the session before the ignition (after-close reports move the next day) to Friday
    df["earnings"] = [earnings_flag(t, index[pos - k - 1], screen_date + pd.Timedelta(days=3))
                      for t, k in zip(df["ticker"], df["consol_days"])]
    df["reason"] = df.apply(reason, axis=1)
    if len(df):
        plot_screen(df, p["close"], screen_date, OUTPUT / f"screen_{screen_date:%Y-%m-%d}.png")

    columns = ["ticker", "direction", "ignition_date", "ignition_sigma", "rel_volume", "consol_days",
               "max_quiet_sigma", "hold", "range_lo", "range_hi", "close_loc", "volume_ratio",
               "consol_excess", "votes", "lean", "earnings", "reason"]
    df = df[columns].round(3)
    df.to_csv(OUTPUT / f"screen_{screen_date:%Y-%m-%d}.csv", index=False)

    print(f"{len(df)} names\n")
    for _, row in df.iterrows():
        flag = "  [earnings]" if row["earnings"] == "yes" else ""
        print(f"{row['ticker']:<6} {row['lean']:<13}{flag}\n       {row['reason']}")


if __name__ == "__main__":
    main()
