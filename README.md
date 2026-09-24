# Deeter Analytics: Quant Research working project

A Thursday-night screen for names that had a high-volume move, then consolidated, with a lean on
whether each one goes again or stalls on Friday. Free data only (yfinance).

## Deliverables

| # | Deliverable | Where |
|---|---|---|
| 1 | Definitions | [`DEFINITIONS.md`](DEFINITIONS.md) |
| 2 | Screen | [`deeter/`](deeter/); latest list in [`output/`](output/) |
| 3 | Evidence | [`EVIDENCE.md`](EVIDENCE.md) |
| 4 | Note to the PM: screen | [`notes/pm_note_screen.md`](notes/pm_note_screen.md) |
| 5 | Note to the PM: alert | [`notes/pm_note_alert.md`](notes/pm_note_alert.md) |

## Run

Requires Python 3.10+ ([python.org](https://www.python.org/downloads/)). From the repo root:

```
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # macOS / Linux
pip install -r requirements.txt

python -m deeter.data       # download prices to data/ (~15 min, once)
python -m deeter.count      # names per week over the sample (no outcomes used)
python -m deeter.screen     # Thursday-night list as of the latest close
python -m deeter.backtest   # evidence over recent weeks
python -m pytest            # rule checks
```

Download after the US close (4pm ET): during market hours yfinance returns a partial bar for
today, which would be treated as a close. To refresh prices, delete `data/prices/` first.

## AI use

I worked in parallel with AI to efficiently find literature, write files, and test code. I was sure to provide as much context as possible before beginning, and I thoroughly validated all AI output.