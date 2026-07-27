# Entry 04 — QuantReturns: "Overnight mean-reversion, Sharpe 4.44 on biotech ETFs"

- status: `VERIFIED`
- registered_at: `2026-07-27T20:08:10Z (git commit timestamp is authoritative)`
- verdict: **SURVIVE** (by literal application of the frozen condition) — reproduced
  gross Sharpe **4.176** (claim 4.44, within tolerance; daily mean 0.2918% vs claimed
  ≈0.29%, t = 18.0), and S_c = **2.745** under the frozen "10 bps per round trip per
  day" flat deduction. See `verification/04/result.md`.
- **verdict-integrity caveat (disclosed, Brier taken)**: the frozen cost wording
  implicitly assumed 100% gross exposure; the disclosed strategy runs 200% gross and
  trades ≈400% notional per day. At a true 5 bps per side **of traded notional** the
  deduction is 20 bps/day and Sharpe drops to **1.313 → the verdict would flip to
  KILL**. Per the no-post-hoc-changes rule the literal frozen reading stands, the
  ambiguity is recorded here at the verdict, and the failed P(kill)=0.85 prediction is
  scored honestly (Brier +0.7225). Break-even: Sharpe crosses 1.0 at ≈5.5 bps/side of
  traded notional — inside opening-auction spread territory. Second-half (2016–2025)
  net Sharpe is 1.57. The registered kill hypothesis is economically vindicated under
  the per-notional reading even though the registered test survives.
- predicted P(kill): **0.85**
- time cap: 3.0 hours
- cash cost cap: ¥0 (free public data only)

## Target claim (frozen quote)

QuantReturns, "Overnight Mean-Reversion" (Substack, published 2025-10-03; mirror at
quantreturns.com/strategy-review/overnight-mean-reversion/):

> A market-neutral strategy trading close-to-open reversals, cross-sectionally
> demeaned; on biotech ETFs (ARKG / XBI / IBB) it reports a daily mean return of
> ≈ 0.29%, t-statistic 17.3, and an annualized **Sharpe of 4.44**.

- Article: https://quantreturns.substack.com/p/overnight-mean-reversion
- Data: ETF daily open/close from Yahoo Finance (free).
- The article assumes execution at the open and close prints; transaction costs are not
  modeled in the headline figure (as far as the published text discloses).

## Primary kill condition (the only verdict-driving test)

Rebuild the strategy from the rules as disclosed in the article, on the three named
biotech ETFs, over the article's stated sample (or the maximal free-data sample if the
article's exact window is ambiguous — the window used will be documented). Compute:

- `S_g`: reproduced **gross** annualized Sharpe (no costs, open/close prints), and
- `S_c`: the same strategy with **5 bps per side** (10 bps per round trip per day)
  deducted — a deliberately conservative floor for liquid-ETF spread + MOO/MOC slippage.

Verdict:

- **KILL** if `S_c < 2.0` (the headline Sharpe 4.44 is predominantly a zero-cost,
  ideal-fill artifact).
- **SURVIVE** if `S_c ≥ 2.0` AND `S_g ≥ 3.44` (gross reproduces to within 1.0 of the
  claim and the result survives the cost floor).
- **REVISE** otherwise (e.g., costs survive but the gross figure does not reproduce).
- **UNVERIFIABLE** if the published rules are insufficient to implement the strategy
  without non-mechanical choices beyond 30 minutes of interpretation (every
  interpretation made will be documented).

## Secondary observations (reported, never verdict-driving)

1. Cost level at which `S_c` crosses 1.0 (break-even cost estimate).
2. Sub-period stability (first half vs. second half of the sample).
3. Short-leg borrow feasibility for the ETFs involved.

## Verification procedure

1. Pin the article text and extract the rules verbatim (30 min).
2. Implement on Yahoo open/close data; reproduce `S_g` (60–90 min).
3. Cost injection for `S_c`; secondary checks; write-up (60 min).

## Kill hypothesis (why P(kill) = 0.85)

The strategy transacts at both the open and the close every day; the open is the most
expensive print of the session, and overnight ETF reversal effects in the literature are
routinely absorbed by one spread. A Sharpe of 4.44 headline with no cost modeling is
the classic shape of a cost-fragile result. Registered before computing anything.
