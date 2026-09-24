# Evidence

_Numbers marked **TODO** are filled in from the 2016–2026 run._

## Verdict

- **The setup has no measurable Friday edge.** Names that ignite on heavy volume and then
  consolidate break out of their quiet range on Friday about as often as ordinary stocks
  in the same position: edge **TODO** points (90% range **TODO**) over **TODO** setups in
  **TODO** weeks.
- **The lean does not add information.** Its apparent power came from where Thursday closed
  in its range, which predicts a Friday break for *any* stock (see
  [the trap I caught](#the-trap-i-caught-close-location)).
- **"Stalls" is the most common outcome** (**TODO**% of setups), in line with the PM's
  "either it goes again Friday, or it stalls."
- **Lead for the next test, not a finding:** these names tend to fade intraday on Friday,
  most clearly after up-moves (**TODO** bps open-to-close).

## What I tested

I ran the screen, unchanged, on every historical Thursday and labelled the next session
(DEFINITIONS.md §5).

| | |
|---|---|
| Sample | **TODO** weeks, **TODO** to **TODO** |
| Primary outcome | Friday close beyond the quiet range: goes again / stalls / reverses |
| Secondary outcome | Friday open-to-close return net of beta × SPY, in the direction of the move |
| Unit of evidence | the **week**: names flagged in the same week share that Friday's market |
| Uncertainty | 90% ranges from resampling whole weeks (5,000 draws) |

**Benchmark.** A narrow range is easy to break in *either* direction, so the goes-again rate
alone says little. The test is **(goes again − reverses)** for the setups minus the same
difference for ordinary universe stocks on the same Friday, with the same number of quiet
days and **closing in the same third of their own range**. That difference is the "edge"
below.

**Comparisons.**
1. Ordinary stocks (the benchmark above).
2. Ignitions that did **not** consolidate, to see whether consolidation adds anything.

Reproduce: `python -m deeter.backtest` (tables in `output/backtest_summary.csv`, one row per
setup in `output/backtest_setups.csv`) and `python -m deeter.grid` (`output/grid.csv`).

## Results

**TODO:** table from `output/backtest_summary.csv`: all setups, up/down, lean groups, each
year, without the 5 busiest weeks, and ignitions that didn't consolidate.

## The trap I caught: close location

My first benchmark matched ordinary stocks on the Friday and the number of quiet days, but
not on where Thursday closed in the range. Against it, the lean looked strong: on 2024–26
data, "Goes" names went again 34% of the time and reversed 3%; "Stalls" names went again 8%
and reversed 29%.

Then I checked ordinary stocks. **TODO** (10-year numbers): a stock that closes in the top
third of its 3-day range breaks above it on the next day about a third of the time and below
it about 3% of the time, setup or not. Closing near an edge simply leaves less distance to
cross. One of the three lean votes is close location, so the lean was measuring geometry.

I added close-third matching to the benchmark after seeing this. It makes the test stricter,
not looser, and changes no screen rule. With it, the lean's edge shrinks to **TODO** ("Goes")
and **TODO** ("Stalls"), and every range includes zero. The unmatched column
(`edge_range_only`) stays in the output so the artifact can be reproduced.

## Robustness

- **By year:** **TODO**. Survivorship bias (below) is smallest in recent years, so those rows
  matter most.
- **Busiest weeks:** the busiest Thursdays (up to **TODO** names) come in market-wide
  sell-offs, when "a few names" becomes many at once. Dropping the 5 busiest weeks gives an
  edge of **TODO**.
- **Consolidation:** ignitions that failed to consolidate have an edge of **TODO**, so the
  quiet days add little.
- **Thresholds:** all 27 combinations in the grid declared in DEFINITIONS.md give an edge of
  **TODO** to **TODO** points, and every range includes zero. The list length varies from
  **TODO** to **TODO** names a week, so the thresholds matter for the list but not for the
  conclusion. Friday open-to-close is negative in **TODO** of 27.

## How to read the ranges

- A 90% range that includes zero is the same as failing a two-sided test at the 10% level,
  with weeks as the unit. I report ranges instead of p-values because they also show **how
  large an edge the data rules out**: with a range of **TODO** to **TODO**, a real edge
  bigger than about **TODO** points would very likely have shown up.
- I did not use a t-test on individual setups. It would treat them as independent, but names
  in the same week move together, so it would overstate precision.
- **Multiple testing:** I looked at about 20 cuts (direction, lean, year, busy weeks,
  comparison) plus 27 grid settings. At a 10% level, a couple of cuts would look
  "significant" by chance alone. That is why the Friday fade is a lead, not a finding.

## The traps

| Trap | How I handled it |
|---|---|
| **Look-ahead** | Every Thursday-side rule uses backward windows only; Friday data is read in one file, `deeter/outcomes.py`. A test (`tests/test_rules.py`) deletes everything after the screen date and checks the setups don't change; I also checked this on real weeks. Beta and σ end the day before they are used. |
| **Survivorship** | Not solved. The universe is **today's** listings, so stocks that delisted during the sample are missing. This is worse the further back the sample goes, and likely flatters down-move setups most (the names that kept falling are the ones now gone). |
| **Thresholds fitted to the answer** | Every threshold was written down with a reason before any outcome was loaded. The only calibration allowed was on names per week, and none was needed. The grid shows all 27 alternatives, and the headline stays the defaults. |
| **Clustered samples** | The week, not the setup, is the unit for every range. |
| **Adjusted prices** | yfinance back-adjusts for splits and dividends, so the $5 and $20M filters use prices adjusted by later dividends. Small effect, near the thresholds only. |
| **Costs** | Not modelled. A liquid name costs roughly **TODO** bps to trade in and out; any edge would need to clear that. With no edge before costs, costs only strengthen the verdict. |

## What free data can't test, and how I would test it

| Gap | Right data |
|---|---|
| Delisted stocks and historical index membership | A point-in-time database with delistings (CRSP, Norgate) |
| Entries after Friday's open (the PM reads the list in the morning) | Minute bars or trades (Polygon, TAQ) |
| Whether the short side of down-moves was tradeable | Borrow availability and fees (securities-lending data) |
| Real "excitement": news, social media, options activity | News and social feeds (RavenPack, StockTwits); options volume (OPRA) |
| Earnings-driven setups (post-earnings drift) | Point-in-time earnings calendars (Wall Street Horizon, I/B/E/S) |
| Real trading costs | The desk's own fills |

## What I'd test next

**TODO** after the 10-year run. Likely: does the Friday intraday fade after up-move setups
hold on minute bars, net of costs, on the period after this sample?
