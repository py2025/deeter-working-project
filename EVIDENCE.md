# Evidence

_Numbers marked **TODO** are filled in from the 2016–2026 run._

**Bottom line:** the setup shows no measurable Friday edge over ordinary stocks, and the lean adds
no information. Any real edge is at most about **TODO** points.

## What happened on Fridays

I ran the screen, unchanged, on every Thursday from **TODO** to **TODO**: **TODO** setups in **TODO**
weeks. A narrow range is easy to break either way, so each setup is compared with ordinary stocks
on the same Friday that closed Thursday in the same third of their own range.
**Edge** = (goes again − reverses) for the setups minus the same for those stocks, in points.
Ranges are 90%, resampling whole weeks, because names in the same week move together.

| | Setups | Goes again | Stalls | Reverses | Edge (90% range) |
|---|---|---|---|---|---|
| All setups | TODO | TODO | TODO | TODO | TODO |
| Up-moves | TODO | TODO | TODO | TODO | TODO |
| Down-moves | TODO | TODO | TODO | TODO | TODO |
| Lean: Goes | TODO | TODO | TODO | TODO | TODO |
| Lean: Stalls | TODO | TODO | TODO | TODO | TODO |
| Ignitions that didn't consolidate | TODO | TODO | TODO | TODO | TODO |

- **The lean is an artifact of where Thursday closed.** Any stock that closes in the top third of
  its range breaks above it next day **TODO**% of the time and below it **TODO**%; setups in the
  same spot do almost exactly the same (`output/close_location.csv`). Before I matched on this, the
  lean looked strong (edge **TODO** for "Goes"); after, it is **TODO**. I added the matching after
  seeing that first result; it makes the test stricter and changes no rule.
- **It holds in every year** (**TODO** to **TODO**) and in all **27** threshold settings of the
  grid (**TODO** to **TODO**; every range includes zero).
- **A lead, not a finding:** Friday's open-to-close return goes against the move, **TODO** bps
  after up-moves (range **TODO**), negative in **TODO** of 27 grid settings. I looked at about 20
  cuts, so one looking "significant" is expected by chance.

## The traps

- **Look-ahead:** Thursday-side rules use backward windows only; Friday is read in one file
  (`deeter/outcomes.py`). A test deletes everything after Thursday and checks the list doesn't change.
- **Survivorship:** not solved. The universe is today's listings, so stocks that delisted since
  2016 are missing. This is worse in earlier years and most likely flatters down-moves (the names
  that kept falling are gone), so recent years carry the most weight.
- **Thresholds fitted to the answer:** every threshold was set before any outcome was loaded. The
  only allowed tuning was names per week (target 3–10); the median was **TODO**, so nothing changed.
  The grid shows all 27 alternatives, and the headline stays the defaults.
- **Costs:** not modelled. With no edge before costs, they only strengthen the verdict.

## What free data can't test

| Gap | How I'd test it |
|---|---|
| Stocks that delisted | Point-in-time database with delistings (CRSP, Norgate) |
| Entering after Friday's open | Minute bars (Polygon, TAQ) |
| Whether down-moves could be shorted | Borrow availability and fees |
| Real attention: news, social, options | News and social feeds; options volume (OPRA) |
| Earnings-driven moves | Point-in-time earnings calendars (I/B/E/S, Wall Street Horizon) |
| Real trading costs | The desk's own fills |

Reproduce: `python -m deeter.backtest` and `python -m deeter.grid`; full tables are in `output/`.
