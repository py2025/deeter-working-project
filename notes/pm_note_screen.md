# Note to the PM: Thursday screen, Sep 24

1. **What it does:** flags stocks that moved at least 2.5σ (unusual for the name, net of the market) on 3× normal volume, then held at least half the move through 2–4 quiet days. Chart: `output/screen_2026-09-24.png`.
2. **MSTR, leans goes:** up 3.2σ on 3.1× volume on Sep 18, four quiet days since. Goes again on a close above 171.19; reverses below 158.29.
3. **BFLY, leans stalls:** up 4.1σ on 3.8× volume on Sep 22, has held 71% of it. Goes again on a close above 10.05; reverses below 8.84.
4. **What history says:** across 546 weeks since 2016, these setups broke their range on Friday no more often than any stock in the same position: about 1 in 6 go again and 2 in 3 stall.
5. **Read the lean as a description, not a forecast:** it only looked predictive because a stock closing near the top of its range is already close to breaking out.
6. **What it doesn't know:** news or sentiment behind the move, anything after Friday's open, whether a short can be borrowed, and stocks that have since delisted.
7. **Tonight's caveats:** MSTR's "volume dried up" vote sits right at the cutoff and today's volume may still be revised; its "quiet" days include a +9% day, quiet only for a stock that volatile.
8. **What I'd test next:** score ignition-day headlines with FinBERT and check whether ignitions with strong sentiment in the direction of the move go again more often than those without.
