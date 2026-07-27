# Verification result — Entry 03 (Concretum VIX strategy)

- executed_at: 2026-07-28 (UTC), local WSL2, cash cost ¥0 (free data/tools only)
- entry: `/home/trow126/falsify-ledger/entries/03-concretum-vix-strategy.md` (unmodified)

## Verdict (mechanical application of the frozen primary kill condition)

**SURVIVE**

- Reproduced full-period Sharpe (5 bps): **0.984** — within ±0.2 of claimed 1.0 (|Δ| = 0.016). PASS (a)
- Sharpe at 15 bps per trade: **0.944** — > 0.7. PASS (b)

## Notebook resolution

- Short link as published: `bit.ly/VIX_Algo_IBKR`
- Resolved URL: `https://colab.research.google.com/drive/1xxb0gW4lIhHGWZNFSP3F8lBsb-nwZqEV?usp=sharing`
- Downloaded copy: `notebook_original.ipynb` (via Drive export of the same file id)
- **Important**: the notebook is a *live-execution template* for IBKR TWS (its own
  banner says it does not run on Colab and requires a local TWS socket). It contains
  **no backtest code** — only the daily signal computation ("Strategy 4") and order
  placement. The full-period backtest was therefore reconstructed from the exact
  rules disclosed in notebook Cell 3 (formulas copied verbatim into `backtest.py`),
  which is the only way to execute the frozen kill condition without a brokerage
  account. This was treated as the permitted mechanical adaptation, not as
  UNVERIFIABLE, because every rule needed (eRV30 formula incl. ddof, 4 regimes,
  VIX/100 sizing, 2% rebalance tolerance, MOC timing) is explicit in the notebook.

## Reproduction setup

- Rules: eRV30 = std(last 10 SPY daily returns, ddof=1)·√252·100; eVRP = VIX − eRV30;
  regimes: (eVRP>0, VIX<VIX3M) → −VIX/100 exposure; (eVRP≤0, VIX<VIX3M) → −0.5·VIX/100;
  (eVRP≤0, VIX>VIX3M) → +VIX/100; else cash. Signal at close t, executed MOC at close t,
  earns day t+1. Rebalance only when drifted weight deviates > 2% from target.
- Traded underlier: 30-day constant-maturity short-term VIX futures excess-return
  index (SPVXSP-style), built from free CBOE daily settles of 208 VX contracts
  (2007-11 … 2025-07). Reconstructed index annualized drift −41.8%/yr (plausible
  for this index family). Exposure is stated in −1x-underlier terms (XIV-like),
  matching the paper's backtest framing; the live notebook uses SVXY (−0.5x, 2×
  notional) + VXX.
- Costs: cost_bps × |traded exposure| on rebalance days.
- Data sources (all free): CBOE `VIX_History.csv`; CBOE `VIX3M_History.csv`
  (starts 2009-09-18) backfilled pre-2009 with Yahoo `^VIX3M` (overlap check on
  3,949 common days: max abs diff 1.05 pts, driven by a handful of stale/rounded
  Yahoo prints; medians agree); SPY adjusted closes via Yahoo/yfinance.
- Period: 2008-01-02 … 2025-05-30 (4,404 trading days), signal warm-up from 2007-11.

## Results

| Metric | Claimed | Reproduced (5 bps) | 15 bps |
|---|---|---|---|
| Annualized return | 16.3% | 15.83% | 15.10% |
| Sharpe | 1.0 | 0.984 | 0.944 |
| Equity (SPY) correlation | ~15% | 0.133 | — |
| Regime mix short/cash/long | 90/6/4% | 89.4/6.7/3.9% | — |
| Max drawdown | (not in frozen quote) | −30.8% (2020-03) | −30.9% |

Cost sensitivity is small because the 2% tolerance band keeps turnover low:
avg one-way turnover 2.50% of NAV/day, trades on only 16.8% of days. Tripling
costs (5→15 bps) shaves ~0.73 pp of annual return and 0.04 of Sharpe. Even the
notebook-faithful SVXY implementation (2× notional per unit of exposure ⇒
effectively doubles the cost per unit exposure) would remain far above the 0.7
Sharpe floor.

## Main reproduction differences (recorded)

1. Backtest reconstructed from disclosed rules; the published notebook itself has
   no backtest (execution template only).
2. Underlier is a self-built SPVXSP-style constant-maturity futures index from CBOE
   settles (S&P's official index history is not freely downloadable); roll weights
   use business-day counting between last trading days, contract expiry taken as
   last-trade-date + 1 day. Small roll-methodology drift vs the official index is
   the largest residual error source; reproduced ann. return is 0.47 pp below claim.
3. VIX3M pre-2009-09 comes from Yahoo backfill (VXV history), not CBOE's file.
4. Sharpe computed as mean/std·√252 with rf = 0 on the excess-return futures index
   (no cash interest credited); the paper's exact convention is unknown.
5. SPY realized vol uses dividend-adjusted closes (as the notebook does via
   IB `ADJUSTED_LAST`).

## Secondary observations (reported, never verdict-driving)

1. Episode drawdowns (5 bps run): 2018-02 Volmageddon **−8.1%** (mild — the eVRP
   filter had cut size / the VIX<VIX3M condition broke early); 2020-03 Covid
   **−30.8%** (this is the full-sample max DD); 2024-08 yen-carry **−5.1%**.
2. Daily-granularity left-tail risk: on days held short, the intraday VIX high
   exceeded the close-to-close VIX move by >30 relative pts on several occasions
   (2013-10-30 +57 pts — possibly a bad CBOE intraday print; 2016-11-09 +38;
   2024-12-20 +34; 2022-01-24 +31; and 2018-02-06 intraday extremes generally).
   A close-only backtest cannot show intraday margin/stop-out losses; the true
   left tail is plausibly deeper than daily closes indicate, but the strategy's
   VIX/100 sizing (larger VIX ⇒ larger allocation is capped at VIX%, i.e. still
   modest notional) limits the amplification.
3. Sub-period stability: 2008–2017 Sharpe **1.334** (ann 19.1%, maxDD −19.4%);
   2018–2025 Sharpe **0.671** (ann 11.6%, maxDD −30.8%). The post-2018 half is
   materially weaker — the headline 1.0 leans on the pre-Volmageddon era. Not
   verdict-driving, but relevant for anyone extrapolating forward.

## Calibration note

Registered prediction was P(kill) = 0.30 (i.e., survive expected). Outcome: SURVIVE.

## Files

- `notebook_original.ipynb` — downloaded published notebook
- `download_data.py` — free-data downloader (CBOE indices, CBOE VX futures, Yahoo SPY/VIX3M)
- `backtest.py` — reproduction backtest (rules verbatim from notebook Cell 3)
- `run_baseline.log` — full execution log (5 bps and 15 bps runs, secondary checks)
- `daily_5bps.csv`, `daily_15bps.csv` — daily return/weight/turnover series
- `data/` — cached raw inputs (VIX_History.csv, VIX3M_History.csv, VIX3M_yahoo.csv, SPY.csv, vx/*.csv)
