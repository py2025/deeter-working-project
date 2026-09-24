# Evidence

**Bottom line:** the setup shows no measurable Friday edge over ordinary stocks, and the lean adds
no information. Any real edge is at most about **2** points.

## What happened on Fridays

I ran the screen, unchanged, on every Thursday from Apr 2016 to Sep 2026: **2,773** setups across **546**
weeks (16 weeks had none). A narrow range is easy to break either way, so each setup is compared with ordinary stocks
on the same Friday that closed Thursday in the same third of their own range.
**Edge** = (goes again − reverses) for the setups minus the same for those stocks, in points.
Ranges are 90%, resampling whole weeks, because names in the same week move together.

| | Setups | Goes again | Stalls | Reverses | Edge (90% range) |
|---|---|---|---|---|---|
| All setups | 2,773 | 16.6% | 68.7% | 14.7% | **+0.3** (−1.2 to +1.7) |
| Up-moves | 1,394 | 17.4% | 67.0% | 15.6% | −1.2 (−3.4 to +1.0) |
| Down-moves | 1,379 | 15.8% | 70.3% | 13.9% | +1.8 (−0.3 to +3.7) |
| Lean: Goes | 527 | 33.4% | 63.9% | 2.7% | +0.8 (−2.6 to +4.0) |
| Lean: Stalls | 254 | 7.9% | 68.1% | 24.0% | −2.7 (−7.7 to +2.2) |
| Ignitions that didn't consolidate | 11,097 | 12.9% | 72.8% | 14.3% | −0.5 (−1.4 to +0.3) |

- **The lean is an artifact of where Thursday closed.** Any stock that closes in the top third of
  its range breaks above it next day **33.9%** of the time and below it **3.6%**; setups in the
  same spot do almost exactly the same (`output/close_location.csv`). Before I matched on this, the
  lean looked strong (edge **+23.1** for "Goes"); after, it is **+0.8**. I added the matching after
  seeing that first result; it makes the test stricter and changes no rule.
- **It holds across years and settings.** Yearly edges run from −2.9 to +4.7; only 2024's range
  excludes zero, about what 11 years produce by chance. All **27** grid settings give −0.6 to +1.7,
  and every range includes zero; the list runs from 2 to 17 names a week, so the thresholds change the
  list, not the conclusion.
- **A lead that didn't survive:** in an earlier run on 2024–26 only, Friday's open-to-close return
  went clearly against up-moves (−35 bps). Over 2016–26 it is −13 bps (−29 to +3.5): the range
  includes zero, and 2022 and 2025 (−35 and −33 bps) carry most of it. I looked at about 20 cuts,
  so a pattern like that is expected by chance.

## The traps

- **Look-ahead:** Thursday-side rules use backward windows only; Friday is read in one file
  (`deeter/outcomes.py`). A test deletes everything after Thursday and checks the list doesn't change.
- **Survivorship:** not solved. The universe is today's listings, so stocks that delisted since
  2016 are missing. This is worse in earlier years and most likely flatters down-moves (the names
  that kept falling are gone), so recent years carry the most weight.
- **Thresholds fitted to the answer:** every threshold was set before any outcome was loaded. The
  only allowed tuning was names per week (target 3–10); the median was 4, so nothing changed.
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
