"""Download and cache daily OHLCV for the universe and SPY (yfinance), recording download dates.

Usage: python -m deeter.data
"""

import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PRICES_DIR = DATA_DIR / "prices"
START = "2016-01-01"  # ~10 years of outcome weeks plus 60+ sessions of warm-up
CHUNK = 200

NASDAQ_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
# Security types that are not common stock. Whole words only, so "Units" is caught but not
# "UnitedHealth". \bunits?\b also drops MLPs ("Common Units"), as the Russell indexes do.
EXCLUDE_NAMES = re.compile(
    r"\bwarrants?\b|\brights?\b|\bunits?\b|\bETNs?\b|preferred|preference|\bnotes? due\b|debenture|%",
    re.IGNORECASE,
)


def _read_symdir(url: str) -> pd.DataFrame:
    text = requests.get(url, timeout=30).text
    lines = [ln for ln in text.splitlines() if not ln.startswith("File Creation Time")]
    return pd.read_csv(io.StringIO("\n".join(lines)), sep="|", dtype=str)


def fetch_symbols() -> pd.DataFrame:
    """Current US-listed common stocks from the Nasdaq Trader symbol directory."""
    nasdaq = _read_symdir(NASDAQ_URL)
    nasdaq = nasdaq.rename(columns={"Symbol": "symbol"})
    nasdaq["exchange"] = "Q"
    other = _read_symdir(OTHER_URL)
    other = other.rename(columns={"ACT Symbol": "symbol", "Exchange": "exchange"})

    cols = ["symbol", "Security Name", "exchange", "ETF", "Test Issue"]
    df = pd.concat([nasdaq[cols], other[cols]], ignore_index=True).dropna(subset=["symbol"])
    df = df[(df["ETF"] == "N") & (df["Test Issue"] == "N")]
    df = df[~df["Security Name"].str.contains(EXCLUDE_NAMES, na=False)]
    df = df[~df["symbol"].str.contains(r"[\$\^=]", regex=True)]
    df["ticker"] = df["symbol"].str.replace(".", "-", regex=False)  # BRK.B -> BRK-B for yfinance
    return df.drop_duplicates("ticker").reset_index(drop=True)


def _to_long(raw: pd.DataFrame) -> pd.DataFrame:
    long = raw.stack(level="Ticker", future_stack=True).reset_index()
    long.columns = [str(c).lower() for c in long.columns]
    return long.dropna(subset=["close"])


def download_prices(tickers: list[str], start: str = START) -> None:
    """Batch download in chunks; each chunk is cached so an interrupted run resumes."""
    PRICES_DIR.mkdir(parents=True, exist_ok=True)
    chunks = [tickers[i : i + CHUNK] for i in range(0, len(tickers), CHUNK)]
    for n, chunk in enumerate(chunks):
        path = PRICES_DIR / f"chunk_{n:03d}.parquet"
        if path.exists():
            continue
        raw = yf.download(chunk, start=start, auto_adjust=True, group_by="column",
                          threads=True, progress=False)
        long = _to_long(raw)
        if long.empty:  # usually a rate limit; saving it would skip these tickers forever
            raise RuntimeError(f"chunk {n + 1} came back empty; wait a few minutes and rerun")
        long.to_parquet(path, index=False)
        print(f"chunk {n + 1}/{len(chunks)} saved", flush=True)


def load_prices() -> dict[str, pd.DataFrame]:
    """Cached prices as wide tables (dates x tickers): open, high, low, close, volume."""
    long = pd.concat(pd.read_parquet(p) for p in sorted(PRICES_DIR.glob("*.parquet")))
    symbols = pd.read_csv(DATA_DIR / "symbols.csv")
    stocks = symbols.loc[~symbols["Security Name"].str.contains(EXCLUDE_NAMES, na=False), "ticker"]
    long = long[long["ticker"].isin(set(stocks) | {"SPY"})]
    fields = ["open", "high", "low", "close", "volume"]
    return {f: long.pivot(index="date", columns="ticker", values=f) for f in fields}


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    symbols = fetch_symbols()
    symbols.to_csv(DATA_DIR / "symbols.csv", index=False)
    tickers = ["SPY"] + [t for t in symbols["ticker"] if t != "SPY"]
    print(f"{len(tickers)} tickers", flush=True)

    download_prices(tickers)

    manifest = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "start": START,
        "n_tickers_requested": len(tickers),
        "symbol_source": [NASDAQ_URL, OTHER_URL],
        "yfinance_version": yf.__version__,
    }
    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("done", flush=True)


if __name__ == "__main__":
    main()
