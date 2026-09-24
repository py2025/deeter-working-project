# Note to the PM: "doing well quickly" alert

**What I'd build:** one alert that fires when a meaningful share of your positions are
ahead by an unusual amount for each name, within the day, *after accounting for market beta*.

**Defaults**

- **"Doing well":** a position is up at least **1σ** of its own typical daily move,
  measured on its return **net of beta × SPY** and in the direction you hold it (a
  short counts when the stock falls). Scaling by each name's volatility means a 2% day
  in KO counts as much as a 6% day in TSLA. Taking out the market matters most: on a
  rally, every long "does well quickly," and that's beta, not your book.
- **"Quickly":** since the prior close, checked every 5 minutes through the session.
  Positions opened today count from their entry price.
- **"Many positions":** at least **30% of open positions, and at least 5 names.** The
  alert says whether it's longs, shorts or both, and which names.

**How often it may fire:** about **once or twice a month** (the top ~5% of days).
I'd set the 1σ and 30% levels by replaying your past positions to hit that rate,
rather than guessing them. That needs your positions and fills history, which I don't
have yet.

**Stopping it crying wolf**

1. **Market-neutral by construction:** the beta adjustment above means a broad rally
   alone can't trigger it.
2. **Once per day at most.** After firing, it re-arms only if the share drops below 20%
   and climbs back over 30%, so it doesn't flicker around the line.
3. **Must persist:** the condition has to hold on two checks in a row (10 minutes), so a
   single bad print or opening spike doesn't fire it.
4. **Monthly review:** I'd log every alert and what you did with it, and move the levels
   if it fires more than planned or you ignore it.

**One question for you:** what do you do when it fires: take profits, add, or look for
news? If a missed alert costs more than a false one, I'd loosen the levels; if false
alarms cost more, I'd tighten them.
