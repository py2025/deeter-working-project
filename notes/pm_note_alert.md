# Note to the PM: "doing well quickly" alert

**What I'd build:** one alert that fires when a meaningful share of your positions are
ahead by an unusual amount for each name, within the day, *after accounting for market beta*.

**Defaults**

- **Doing well:** up at least **1σ** of the name's typical daily move, net of beta × SPY, in the
  direction you hold it. On a rally every long "does well"; that's beta, not your book.
- **Quickly:** since the prior close (or since entry, for positions opened today), checked every
  5 minutes.
- **Many positions:** at least **30%** of open positions and at least **5** names. The alert says
  which names, and whether it's longs, shorts or both.

**How often:** about once or twice a month. I'd set the 1σ and 30% by replaying your past
positions to hit that rate, which needs your positions history.

**Not crying wolf:** a broad rally can't trigger it (beta is removed); at most once a day; it must
hold on two checks in a row; after firing, it re-arms only once the share drops below 20%. I'd
review every alert monthly and move the levels if it fires more than planned.

**One question for you:** what do you do when it fires? If a missed alert costs more than a false
one, I'd loosen the levels; if not, tighten them.
