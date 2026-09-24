# Definitions

Every threshold was fixed before any Friday outcome was loaded, and uses only data up to
Thursday's close. The values are in `deeter/config.py` under the names shown.

**Universe:** US-listed common stocks, price above **$5** (`min_price`), 20-day median dollar volume
at least **$20M** (`min_dollar_volume`), 61+ sessions of history.
*Why:* below $5, moves are more often noise; $20M a day lets a ~$200k position trade at 1% of
volume (the PM's real size should set this).

## "Everyone is excited about"

**Rule:** excess return at least **2.5σ** of the stock's own
stock-specific volatility (`ignition_sigma`; beta and σ from the prior 60 sessions), in the same
direction as the raw move.
*Why 2.5σ:* unusual *for this stock* (a 5% day is routine for TSLA, news for KO); it fires on ~3% of
trading days, while 2.0σ would fire about monthly for every name.
*Two meanings:* real attention (news, social, options) or a price-and-volume shock; free data only
has the second. Up-moves only, or both; I use both, reported separately (long/short book).

## "With volume"

**Rule:** volume at least **3×** its 50-day median (`volume_mult`).
*Why 3×:* the top ~2.5% of stock-days; an extreme return on extreme volume is the standard proxy for
an attention shock (Barber & Odean 2008).
*Two meanings:* unusual for the stock (my reading) or large in absolute terms; the $20M liquidity
floor covers the second.

## "A few consolidation days"

**Rule:** **2–4** sessions after the ignition, up to Thursday (`consol_min`, `consol_max`); each one
within **1σ** (`consol_sigma`); Thursday's close keeps at least **50%** of the ignition move
(`min_hold`).
*Why:* one quiet day is noise and more than four is stale; 1σ is an ordinary day; giving back more
than half means the market rejected the move.
*Two meanings:* a tight range or holding the gains; I require both. An ignition this week only, or
last week too; counting 2–4 sessions back reaches the prior Friday.

## "Goes again" vs. "stalls"

**Rule:** Friday closes **beyond the quiet range** (the high and low of the consolidation days) in
the direction of the move = goes again; inside it = stalls; beyond the other side = reverses.
*Why:* a close outside the range is the plain meaning of "goes again," and closes avoid intraday
noise.
*Two meanings:* breaking the range or any gain on Friday; close-to-close (includes the overnight
gap) or open-to-close (tradeable after reading the list). The range break decides; I also report
Friday's open-to-close return net of beta × SPY.

## "Leaning"

**Rule:** three equal votes, mirrored for down-moves: Thursday closed in the **top third** of the
range; quiet-day volume at most **50%** of the ignition day's; the stock **beat SPY** over the quiet
days. 3 votes = Goes, 2 = Leans goes, 1 = Leans stalls, 0 = Stalls.
*Why:* each is a simple sign that buyers are still in control; thirds and halves are plain splits,
and the weights are equal because fitting them would need the outcomes.
*Two meanings:* a forecast or a description of the chart. It's built as the second; whether it
forecasts is tested in [`EVIDENCE.md`](EVIDENCE.md).

**Earnings:** names with an earnings date between the day before the ignition and Friday are
flagged, not dropped, because yfinance's history of earnings dates isn't reliable enough to filter on.
