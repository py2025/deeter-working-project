# Definitions

These rules turn the PM's message into something a machine can run. They were fixed **before any
Friday outcome was loaded**. Every threshold has a number, a one-line reason, and the type of that
reason:

- **[M] mechanism:** why the market should behave this way
- **[S] statistics:** what the number means as a frequency or error bar
- **[P] practical:** capacity, or the PM's request for "a few" names
- **[C] convention:** the weakest; used only as a tiebreak

> "Every week there are a few names everyone is excited about with volume, but then there are a few
> consolidation days. From there, either it goes again Friday, or it stalls."

## The idea behind the rules

A big move on heavy volume has one of two causes. A **liquidity-driven** move happens because
someone needed to trade; the price gets pushed and then reverts (Campbell, Grossman & Wang 1993).
An **information-driven** move is a repricing, and it continues (Llorente, Michaely, Saar & Wang
2002). The consolidation days are how I tell them apart: a liquidity-driven move usually gives back
its gains within a few days, while an information-driven move holds them as volume fades. The
screen looks for moves that pass that test by Thursday night. The backtest checks whether passing it
tells me anything about Friday.

## Notation

For each stock, on trading session `t`: open `O_t`, high `H_t`, low `L_t`, close `C_t`, volume `V_t`.
All prices are split- and dividend-adjusted.

- Return: `r_t = C_t / C_{t-1} - 1`
- Beta: `β_t` from an OLS regression of `r` on SPY's return over sessions `t-60 … t-1`
- Excess return: `e_t = r_t - β_t · r_SPY,t`
- Volatility: `σ_t` = standard deviation of the regression residuals over sessions `t-60 … t-1`

Every estimate ends the session *before* the day it is applied to, so a day never counts toward its
own yardstick.

**Weeks.** The outcome day `D` is the last trading session of the calendar week (normally Friday).
The screen date `S` is the session before `D` (normally Thursday). Everything is counted in
sessions, so holiday weeks need no special cases.

## 1. Universe: liquid US common stocks

Measured as of the session before the ignition day (`I-1`):

| Rule | Parameter | Value | Why |
|---|---|---|---|
| Price | `min_price` | `C_{I-1} > $5` | [M] Below $5, spreads and the minimum tick are large relative to price and many institutions can't hold the stock, so moves there are more often microstructure noise than attention. |
| Liquidity | `min_dollar_volume` | 20-day median of `C·V` ≥ $20M | [P] At 1% of daily volume, this supports roughly a $200k position without moving the price much. **The PM's real position size should set this; it is a question for the PM.** A median, so one spike can't qualify a stock. |
| History | `min_history` | ≥ 61 sessions | [S] The 60-session beta and σ need a full window. This excludes recent IPOs, and I say so. |

The candidate list is every **currently** US-listed common stock in the Nasdaq Trader symbol
directory (`nasdaqlisted.txt` and `otherlisted.txt`). ETFs, test issues, warrants, rights, units,
preferreds, notes and ETNs are excluded by security type. The price and liquidity rules then remove
most closed-end funds, SPACs and micro-caps. I planned to use Russell 3000 holdings, but iShares
blocks scripted downloads of its holdings file. The directory is a superset of the Russell 3000, so
it also catches smaller names the crowd gets excited about. Either list introduces **survivorship
bias**: stocks that collapsed or delisted during the sample period are missing (see
[Known limitations](#known-limitations)).

## 2. "Everyone is excited about": the ignition day

Session `I` is an ignition day if:

| Rule | Parameter | Value | Why |
|---|---|---|---|
| Unusual move | `ignition_sigma` | `\|e_I\| ≥ 2.5 · σ_I` | [M] Scaling by volatility means "exciting" is *unusual for this stock*: a 5% move is routine for TSLA and news for KO. [S] 2.5σ is about 1.2% of days under a normal distribution, roughly once a quarter per stock. Fat tails make it more common: the counting pass measured **3.0%** of stock-days in the universe. 2.0σ would be once a month per stock even under a normal distribution, too common across ~1,680 names (the measured median) to mean "everyone is excited." |
| Relative to the market | (uses `e`, not `r`) | beta-adjusted | [M] On a day SPY rises 3%, every low-volatility stock clears 2.5σ. That is the market, not excitement about a name. |
| Same direction | — | `sign(r_I) = sign(e_I)` | [M] A high-beta stock can fall 2% on a day SPY falls 3% and still have a large *positive* excess return. That isn't a move anyone is excited about, and "holds the move" (§4) would be meaningless for it. Added while writing the code, before any outcome was loaded. |
| Volatility window | `vol_window` | 60 sessions | [S] About a quarter. The error in the σ estimate is about 1/√(2·60) ≈ 9%, stable enough while still adapting to regime changes. |

The **direction** of the setup is `d = sign(e_I)`: +1 for an up-move, −1 for a down-move. Both
directions are screened, and the backtest reports them **separately as well as pooled**, because
crowd psychology on the way up (attention, FOMO) may not mirror the way down (panic, forced
selling).

## 3. "With volume"

| Rule | Parameter | Value | Why |
|---|---|---|---|
| Volume spike | `volume_mult` | `V_I ≥ 3 × median(V_{I-50} … V_{I-1})` | [M] Extreme volume with an extreme return is the standard proxy for an attention shock (Barber & Odean 2008), and high-volume stocks tend to rise afterwards (Gervais, Kaniel & Mingelgrin 2001). [S] Daily log volume has a standard deviation of roughly 0.4–0.5, so 3× (ln 3 ≈ 1.1) falls around the top 1–3% of days. The counting pass measured **2.5%**. |
| Baseline window | `volume_window` | 50 sessions | [C] Matches the ~50-day reference window in Gervais, Kaniel & Mingelgrin. A median, so one earlier spike doesn't raise the bar. |

## 4. "A few consolidation days"

The consolidation days are sessions `I+1 … S`. There are `k = S − I` of them. All of the following
must hold:

| Rule | Parameter | Value | Why |
|---|---|---|---|
| How many days | `consol_min`, `consol_max` | `2 ≤ k ≤ 4` | [S] One quiet day is noise; two is the minimum that shows a pattern. [M] Older than four days is stale, because attention effects fade within days. In a normal week this puts the ignition between the prior Friday and Tuesday. |
| Quiet days | `consol_sigma` | every `\|e_j\| < 1.0 · σ_I` | [S] 1σ covers about 68% of ordinary days, so no consolidation day was news in its own right. σ is fixed at its ignition-day value so the yardstick doesn't move. |
| Holds the move | `min_hold` | `(C_S − C_{I-1}) / (C_I − C_{I-1}) ≥ 0.5` | [M] Giving back more than half the move means the market rejected it: the liquidity reversal described above. 0.5 simply means "kept more than it gave back." It is **not** a Fibonacci level. This uses raw price, which is what the PM sees on the chart. |

The **consolidation range** is `R_hi = max(H_j)` and `R_lo = min(L_j)` over `j = I+1 … S`. It
excludes the ignition day.

These rules allow **at most one** valid ignition per stock per week: a second ignition inside the
window would be a day of `|e| ≥ 2.5σ`, which breaks the quiet-day rule for the first one.

## 5. "Goes again" vs. "stalls": the Friday outcome

Written for `d = +1`. For `d = −1`, flip the direction (a break below `R_lo` counts as going again).

**Primary outcome (decides the verdict):**

| Label | Rule |
|---|---|
| Goes again | `C_D > R_hi`: closes beyond the range in the direction of the ignition |
| Stalls | `R_lo ≤ C_D ≤ R_hi`: closes inside the range |
| Reverses | `C_D < R_lo`: closes beyond the range against the ignition |

[M] A close outside the range is the plain meaning of "goes again," and using closes avoids intraday
noise.

**Secondary outcome (reported, but does not decide the verdict):**

- Friday open-to-close excess return, in the direction of the setup:
  `d · [(C_D / O_D − 1) − β · (C_SPY,D / O_SPY,D − 1)]`.
  [P] The PM reads the list Friday morning, so this is the part of Friday that can actually be
  traded.
- For information only: close-to-close `d · e_D`, and the overnight gap `d · (O_D / C_S − 1)`.

**Why fix the primary in advance:** with more than one outcome measure, reporting whichever looks
better afterwards is a quiet form of fitting to the answer.

## 6. "Leaning"

Three equal-weight votes, using only data up to `S`'s close. Written for `d = +1` and mirrored for
`d = −1`.

| Vote | Parameter | Rule | Why |
|---|---|---|---|
| (a) Close location | `lean_close_loc` | `(C_S − R_lo) / (R_hi − R_lo) ≥ 2/3` (≤ 1/3 when `d = −1`) | [M] Closing near the top of the range means buyers were in control at the end. [C] Thirds are a deliberately simple split, not a fitted one. If `R_hi = R_lo`, this vote is 0. |
| (b) Volume dry-up | `lean_volume_ratio` | `mean(V_{I+1} … V_S) ≤ 0.5 · V_I` | [M] Fading volume fits the story that profit-taking has been absorbed; low-volume moves tend to continue while high-volume moves reverse (Conrad, Hameed & Niden 1994). |
| (c) Strength vs. market | — | `d · Σ e_j > 0` over the consolidation days | [M] The stock rose or held against the market while it was consolidating. |

| Votes | Lean |
|---|---|
| 3 | Goes |
| 2 | Leans goes |
| 1 | Leans stalls |
| 0 | Stalls |

[S] **Why equal weights:** choosing weights requires outcome data, which would be fitting. Unit
weights often do as well as fitted ones out of sample (Dawes 1979).

**The lean is a starting view, not a proven edge.** The backtest checks whether it tells "goes
again" and "stalls" apart at all.

## 7. Earnings flag

A name is **flagged, not excluded**, if yfinance reports an earnings date between `I−1` and `D`.
[M] An earnings-driven move brings a different, well-documented effect (post-earnings drift;
Bernard & Thomas 1989). [P] I flag rather than filter because yfinance's historical earnings dates
aren't reliable enough to filter on.

## Evidence protocol (fixed in advance)

- **Sample:** every complete week the data allows after the 60-session warm-up: **128 weeks**
  (screen dates Apr 11, 2024 to Sep 17, 2026). Set by the counting pass, before any outcome was
  loaded.
  [S] With 128 independent weeks, the standard error of a hit rate is about 4.4 percentage points,
  so the test can see a gap of about 9 points from the base rate and nothing much smaller.
- **Unit of evidence is the week, not the signal.** Names flagged in the same week move together.
  Uncertainty ranges come from resampling whole weeks.
- **Comparisons:**
  1. All universe names on the same outcome days (secondary outcome), to show what an ordinary
     Friday looks like.
  2. Ignitions that had no valid consolidation (secondary outcome), to show whether consolidation
     adds anything.
- **Sensitivity grid, declared now and reported in full:** `ignition_sigma` ∈ {2.0, 2.5, 3.0} ×
  `volume_mult` ∈ {2, 3, 4} × `min_hold` ∈ {0.33, 0.5, 0.67}. The headline stays the default
  settings above, whatever the grid shows.

### Calibration: allowed only on counts

The PM asked for "a few" names. Before any outcome is loaded, a counting pass runs the filters over
the sample and reports **names per week only**. The target is a median of **3–10 names per week**.
If the count is outside that range, the thresholds may be adjusted, and every change is logged
below with the counts that caused it. Thresholds are **never** adjusted on Friday outcomes.

| Date | Change | Reason (counts only) |
|---|---|---|
| 2026-09-23 | **None.** Every threshold kept as written. | Median 6 names a week (middle half 4–9, range 1–25, no empty weeks) over 128 weeks: inside the 3–10 target. Output: `output/counts_per_week.csv`. |

## Where the PM's words could mean two things

| Words | Reading A | Reading B | My choice |
|---|---|---|---|
| "Everyone is excited" | Price and volume shock | Real attention (news, social media, options flow) | A, because B isn't available in free data; volume is my proxy. |
| "Everyone is excited" | Up-moves only | Both directions | Both, reported separately (long/short book). |
| "Every week" | Ignition in the same week | Ignition in the prior week too | Counted in sessions: 2–4 quiet days before Friday, which reaches back to the prior Friday. |
| "Consolidation" | Tight range | Holds its gains | Both are required. |
| "Goes again" | Breaks out of the range | Any positive Friday return | Range break is primary; return is secondary. |
| "Goes again Friday" | Close-to-close (includes the overnight gap) | Open-to-close (tradeable after reading the list) | Both reported; open-to-close is the secondary outcome. |
| "Stalls" | Stays inside the range | Anything that isn't "goes again" | Stalls and reverses are kept separate. |

## Known limitations

- **Survivorship:** the universe is built from today's listings, so names that delisted during the
  sample are missing. This probably flatters down-move setups most, since the stocks that kept falling are
  the ones likely to be gone.
- **Adjusted prices:** yfinance back-adjusts for splits and dividends. This is fine for returns, but
  the $5 price filter is applied to adjusted prices, which can differ from what traded at the time.
- **No intraday data:** I can't test entries after Friday's open, only open-to-close.
- **No real attention data:** news, social media and options flow aren't in free data.
- **Unreliable earnings dates** (see §7).
- **No borrow data:** the short side of down-move setups may not have been tradeable.

## References

- Barber, B. & Odean, T. (2008). All that glitters: the effect of attention and news on the buying
  behavior of individual and institutional investors. *Review of Financial Studies*.
- Bernard, V. & Thomas, J. (1989). Post-earnings-announcement drift: delayed price response or risk
  premium? *Journal of Accounting Research*.
- Campbell, J., Grossman, S. & Wang, J. (1993). Trading volume and serial correlation in stock
  returns. *Quarterly Journal of Economics*.
- Conrad, J., Hameed, A. & Niden, C. (1994). Volume and autocovariances in short-horizon individual
  security returns. *Journal of Finance*.
- Dawes, R. (1979). The robust beauty of improper linear models in decision making. *American
  Psychologist*.
- Gervais, S., Kaniel, R. & Mingelgrin, D. (2001). The high-volume return premium. *Journal of
  Finance*.
- Llorente, G., Michaely, R., Saar, G. & Wang, J. (2002). Dynamic volume-return relation of
  individual stocks. *Review of Financial Studies*.
