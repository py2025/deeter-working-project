"""Thursday-night list as of the latest close, or as of a past date.

Usage: python -m deeter.screen [YYYY-MM-DD]
"""

import sys
from pathlib import Path

import pandas as pd
import yfinance as yf

from deeter.config import Config
from deeter.data import load_prices
from deeter.rules import find_setups

OUTPUT = Path(__file__).resolve().parent.parent / "output"
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


def main() -> None:
    cfg = Config()
    p = load_prices()
    index = p["close"].index
    screen_date = pd.Timestamp(sys.argv[1]) if len(sys.argv) > 1 else index[-1]
    print(f"Screen as of the {screen_date:%A %Y-%m-%d} close")
    if screen_date.weekday() != 3:
        print("Note: not a Thursday. The list assumes the next session is the outcome day.")

    df = find_setups(p, cfg, [screen_date])
    pos = index.get_loc(screen_date)
    df["ignition_date"] = [index[pos - k] for k in df["consol_days"]]
    # From the session before the ignition (after-close reports move the next day) to Friday
    df["earnings"] = [earnings_flag(t, index[pos - k - 1], screen_date + pd.Timedelta(days=3))
                      for t, k in zip(df["ticker"], df["consol_days"])]
    df["reason"] = df.apply(reason, axis=1)

    columns = ["ticker", "direction", "ignition_date", "ignition_sigma", "rel_volume", "consol_days",
               "max_quiet_sigma", "hold", "close_loc", "volume_ratio", "consol_excess", "votes",
               "lean", "earnings", "reason"]
    df = df[columns].round(3)
    df.to_csv(OUTPUT / f"screen_{screen_date:%Y-%m-%d}.csv", index=False)

    print(f"{len(df)} names\n")
    for _, row in df.iterrows():
        flag = "  [earnings]" if row["earnings"] == "yes" else ""
        print(f"{row['ticker']:<6} {row['lean']:<13}{flag}\n       {row['reason']}")


if __name__ == "__main__":
    main()
