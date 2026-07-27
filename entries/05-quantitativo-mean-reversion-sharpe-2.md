# Entry 05 — Quantitativo: "A mean reversion strategy with a 2.11 Sharpe"

- status: `VERIFIED`
- registered_at: `2026-07-27T20:08:10Z (git commit timestamp is authoritative)`
- verdict: **KILL** — on real QQQ data the faithful reconstruction (MDD and
  time-in-market match the article) yields gross Sharpe **0.749** and cost-adjusted
  **0.622** < 1.0. Interpretation-invariant across all documented alternatives
  (0.54–0.78). Diagnosis (non-verdict): the claimed 2.11 is consistent with an
  invested-days-only Sharpe convention (reproduced invested-only: 1.92 gross) plus
  synthetic pre-1999 data — a convention, not a tradable full-series Sharpe. See
  `verification/05/result.md`.
- predicted P(kill): **0.70**
- time cap: 3.0 hours
- cash cost cap: ¥0 (free public data only)

## Target claim (frozen quote)

Quantitativo, "A mean reversion strategy with 2.11 Sharpe":

> A mean-reversion strategy on QQQ (with a PSQ variant) using a 25-day average-range
> band, IBS < 0.3 entry filter, a 300-day SMA regime filter, and an exit on the close
> above the previous day's high; backtested 1993–2024: **Sharpe 2.11, annualized
> 13.0%, max drawdown −20.3%** (variant: Sharpe 2.02 / 8.9% ann.).

- Article: https://www.quantitativo.com/p/a-mean-reversion-strategy-with-211
- Data: QQQ / PSQ daily OHLC from Yahoo Finance (free). Note QQQ launched 1999-03 and
  PSQ 2006-06; the article's 1993 start implies synthetic pre-inception data. The
  reproduction uses real ETF data from inception; the window difference is documented,
  not penalized.
- Transaction costs are not modeled in the headline figure (as far as the published
  text discloses).

## Primary kill condition (the only verdict-driving test)

Rebuild the long-QQQ variant from the rules as disclosed in the article, on real QQQ
data (1999-03 onward, Yahoo adjusted OHLC). Compute:

- `S_g`: reproduced gross annualized Sharpe (no costs), and
- `S_c`: the same strategy with **5 bps per side** deducted on every entry and exit.

Verdict:

- **KILL** if `S_c < 1.0` (the claim's economic content does not survive a
  conservative cost floor).
- **SURVIVE** if `S_c ≥ 1.5` AND `S_g ≥ 1.6` (within ~0.5 of the claimed 2.11 on the
  real-data window).
- **REVISE** otherwise.
- **UNVERIFIABLE** if the published rules are insufficient to implement without
  non-mechanical choices beyond 30 minutes of interpretation (all interpretations
  documented).

## Secondary observations (reported, never verdict-driving)

1. Sensitivity to the three magic numbers (2.5× range multiplier, IBS 0.3, SMA 300):
   ±20% perturbation of each, one at a time.
2. Sub-period Sharpe (dot-com, 2008, post-2020).
3. Time-in-market and trade count (exposure-adjusted return).

## Verification procedure

1. Pin article text, extract rules (30 min).
2. Implement and reproduce `S_g` on real QQQ data (60–90 min).
3. Cost injection, perturbations, write-up (60 min).

## Kill hypothesis (why P(kill) = 0.70)

A high-turnover mean-reversion overlay with three tuned constants and no cost modeling
typically loses 0.5–1.0 Sharpe to a 10 bps round trip; whether it lands above or below
the 1.0 floor is genuinely uncertain — hence a lower P(kill) than entries 01/02/04.
Registered before computing anything.
