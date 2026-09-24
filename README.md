# Deeter Analytics: Quant Research working project

A Thursday-night screen for names that had a high-volume move, then consolidated, with a lean on
whether each one goes again or stalls on Friday. Free data only (yfinance).

**Result:** the setup shows no measurable Friday edge over ordinary stocks, and the lean's apparent
power turns out to be an artifact of where Thursday closed in its range. See
[`EVIDENCE.md`](EVIDENCE.md).

## Deliverables

| # | Deliverable | Where |
|---|---|---|
| 1 | Definitions | [`DEFINITIONS.md`](DEFINITIONS.md) |
| 2 | Screen | code in [`deeter/`](deeter/); Today's (09/24/26) list in [`output/`](output/) as a chart (`screen_2026-09-24.png`) and a table (`screen_2026-09-24.csv`). `screen_2025-09-25.*` is an example of a busier week (10 names). |
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

python -m deeter.data       # download prices since 2016 to data/ (~4 min, once)
python -m deeter.count      # names per week over the sample (no outcomes used)
python -m deeter.screen     # Thursday-night list as of the latest close
python -m deeter.screen 2025-09-25   # ...or as of any past date
python -m deeter.backtest   # evidence: every Thursday since 2016 (~3 min)
python -m deeter.grid       # the same for 27 threshold settings (~20 min)
python -m pytest            # rule checks
```

Download after the US close (4pm ET): during market hours yfinance returns a partial bar for
today, which would be treated as a close. To refresh prices, delete `data/prices/` first.

## AI use

I worked with AI to find literature and turn my ideas into files (.md + .py) + tests; I provided as much context as possible. Manually validated output, tested, and analyzed results.