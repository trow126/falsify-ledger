# Entry 04 verification result — QuantReturns "Overnight Mean-Reversion" (CO-OC, biotech ETFs)

- executed_at: 2026-07-28
- executor: Claude (falsify-gate verification task)
- entry: `/home/trow126/falsify-ledger/entries/04-quantreturns-overnight-sharpe-4.md` (frozen, unmodified)
- article snapshots: `article_mirror.html` / `article_substack.html` (fetched 2026-07-28; text
  extractions `article_mirror.txt` / `article_substack.txt`)

## 1. Rule extraction (verbatim quotes from the article)

Source: https://quantreturns.com/strategy-review/overnight-mean-reversion/ (published Oct 3, 2025;
identical strategy text on the Substack mirror).

Signal and direction:

> "we take a look at **overnight–intraday mean-reversion**, denoted **CO-OC**. In plain terms, we
> **buy assets with low past overnight returns and sell assets with high past overnight returns**,
> then hold those positions **during the next intraday session**."

Portfolio construction:

> "1. For each day, we compute the **formation returns** across the universe and **demean** them
> cross-sectionally.
> 2. Demeaning has a great property: the **signals sum to zero**. If we map signal → weight
> linearly, the **weights also sum to zero**.
> 3. Result: an **equal-weight long/short, market-neutral** portfolio with very low market risk by
> construction.
> 4. We then double the weight of each asset, so we invest 100% of the Portfolio Value in long and
> -100% short, keeping us market neutral."

Outlier handling:

> "We Winsorize the returns two-sided to keep outliers from dominating, then evaluate summary
> statistics, t-stats and annualized Sharpe for each setup."

Target claim (biotech ETF universe):

> "Below are the results for the strategies using Equity Biotech ETF's (ARKG, XBI and IBB): ...
> the **CO–OC strategy** stands out again with the strongest performance: an average daily return
> of ~0.29%, a very high t-stat (17.3), and an annualised Sharpe ratio of 4.44."

Sample period: the stats-table section states no window (tables are images), but the backtest
section for the same universe states **Start Date 2007-01-01, End Date 2025-09-01**, and the
conclusion says "Backtests over 2007–2025". This window was used.

Execution assumption (article's own caveat):

> "both the signal and the execution depend on the opening price. To implement it correctly, you
> need to know the precise open in order to size trades — but you also need to trade at that very
> same open. ... even a short delay — such as executing one or five minutes after the open, can
> erode most or all of the edge."

Snapshot discrepancy noted (not verdict-relevant): for the *financials* universe the mirror says
Sharpe "above **9.0**" while the Substack says "above **7.1**".

## 2. Interpretations made (all of them; total interpretation effort well under 30 min)

1. **Formation return**: CO_i(t) = Open_i(t) / Close_i(t−1) − 1 (same-day overnight return;
   position formed at today's open, held to today's close). Directly stated by the article.
2. **Weights**: linear map, reversal sign: s_i = −(CO_i − mean_universe(CO)); w_i = 2·s_i / Σ|s_j|,
   giving +100% long / −100% short (gross 200%). The article's "equal-weight long/short" phrase
   conflicts with "map signal → weight linearly"; the linear reading was used and is validated by
   the near-exact reproduction of the claimed stats (see §3).
3. **Winsorization**: level undisclosed. Primary run: two-sided 1%/99% on each ETF's formation
   return series (full-sample quantiles). Sensitivity at none and 5%/95% reported — the result
   barely depends on it (gross Sharpe 4.26 / 4.18 / 3.88).
4. **Universe availability**: ARKG's first Yahoo data day is 2014-10-31, so 2007–2014 has only
   XBI+IBB. Demeaning was done over the assets available each day (≥2 required). 1,973 two-asset
   days, 2,722 three-asset days. The article does not say how it handled ARKG's late inception;
   demeaning over available assets is the only implementable reading of "compute formation returns
   across the universe" for that period.
5. **Data adjustment choice**: yfinance `auto_adjust=True`, i.e. Open and Close are both adjusted
   by the same per-day split/dividend factor. This keeps the intraday ratio Close/Open identical
   to the raw ratio and makes the overnight ratio Open_t/Close_{t−1} economically correct across
   ex-dividend and split dates. (Raw-vs-raw would misstate overnight returns on ex-div/split days.)
6. **Sharpe/t-stat conventions**: annualization √252; t = mean/std·√N; zero risk-free (matches the
   article's apparent convention).
7. **Cost deduction (S_c)**: the frozen entry says "**5 bps per side** (10 bps per round trip per
   day) deducted". The strategy's gross exposure is 200%, so "5 bps per side of traded notional"
   would be 400% notional/day × 5 bps = 20 bps/day of NAV, while the entry's own parenthetical
   fixes the deduction at **10 bps per day**. The parenthetical is the frozen quantification, so
   the verdict-driving S_c uses a **flat 10 bps/day** deduction; the 20 bps/day per-notional
   reading is reported as a sensitivity. **This ambiguity is verdict-flipping — see §5.**

## 3. Results

Sample used: 2007-01-03 .. 2025-08-29 (N = 4,695 trading days), Yahoo Finance daily open/close.

| Quantity | Reproduced | Article claim |
|---|---|---|
| Mean daily return (gross) | **0.2918%** | ~0.29% |
| t-stat (gross) | **18.03** | 17.3 |
| **S_g** (gross annualized Sharpe) | **4.176** | 4.44 |
| **S_c** (net, flat 10 bps/day — frozen reading) | **2.745** | — |
| S_c under per-notional 20 bps/day reading | 1.313 | — |

The gross claim **reproduces**: |4.176 − 4.44| = 0.26 < 1.0, and mean/t-stat are essentially exact.

Winsorization sensitivity (gross / net-10bps Sharpe): none 4.26 / 2.83; 1–99% 4.18 / 2.74;
5–95% 3.88 / 2.46.

## 4. Frozen verdict (mechanical application)

- KILL if S_c < 2.0 → 2.745 ≥ 2.0, not triggered.
- SURVIVE if S_c ≥ 2.0 AND S_g ≥ 3.44 → 2.745 ≥ 2.0 ✓ and 4.176 ≥ 3.44 ✓.

**Verdict: SURVIVE** (under the frozen entry's literal cost quantification of 10 bps/day).

## 5. Verdict-integrity caveat (must be read with the verdict)

The frozen cost floor was written as "5 bps per side (10 bps per round trip per day)", which
implicitly assumes 100% gross. The disclosed strategy runs 200% gross and trades the full book in
at the open and out at the close (≈400% traded notional/day). At a true 5 bps per side of traded
notional the deduction is 20 bps/day and **S_c = 1.313 < 2.0 → the verdict would be KILL**. The
registered kill hypothesis ("absorbed by one spread") is economically vindicated by the
per-notional reading even though the frozen literal reading yields SURVIVE. The mechanical verdict
above follows the frozen text; the discrepancy is recorded here and left to the ledger owner —
the entry itself was not modified.

## 6. Secondary observations (never verdict-driving)

1. **Break-even cost** (gross mean 29.18 bps/day, daily vol 1.109%):
   net Sharpe = 2.0 at 15.2 bps/day deduction; **net Sharpe = 1.0 at 22.2 bps/day**; zero at
   29.2 bps/day. Expressed per side of traded notional (÷4 at gross 200%): Sharpe 1.0 breaks at
   ≈ 5.5 bps/side — i.e. the strategy dies inside quoted-spread territory for the open auction.
2. **Sub-period stability**: strong decay. H1 (2007-01..2016-04): gross Sharpe 6.24, mean 35.8
   bps/d. H2 (2016-05..2025-08): gross Sharpe 2.81, mean 22.6 bps/d. Net-10bps: H1 4.49 vs
   **H2 1.57** — the second half alone would fail the S_c ≥ 2.0 bar even under the lenient cost
   reading.
3. **Short-leg borrow feasibility**: positions are intraday-only (open→close), so no overnight
   borrow cost accrues, but US reg-SHO locates are still required to short. XBI and IBB are
   large, liquid, generally easy-to-borrow ETFs; ARKG is smaller (AUM well under $2B post-2022)
   with periodically tighter borrow. The binding practicality issue is not borrow but the
   article's own caveat: the signal requires the opening print to size the trade while
   simultaneously executing at that same print (opening-auction access), which retail cannot do.

## 7. Files

- `article_mirror.html` / `article_substack.html` — raw snapshots (2026-07-28)
- `article_mirror.txt` / `article_substack.txt` — text extractions
- `reproduce.py` — full reproduction code (yfinance, auto_adjust=True)
- `logs/run1.log` — execution log of the run reported above
- `data/prices_adj.pkl` — cached Yahoo price data; `data/strategy_daily_returns.csv` — daily
  gross strategy returns
- `venv/` — Python environment (yfinance 등)
