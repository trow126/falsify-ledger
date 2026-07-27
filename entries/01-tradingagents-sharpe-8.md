# Entry 01 — TradingAgents: "Sharpe 8.21 on AAPL"

- status: `REGISTERED (result not yet observed)`
- registered_at: `2026-07-27T19:41:56Z (git commit timestamp is authoritative)`
- verdict: —
- predicted P(kill): **0.90**
- time cap: 3.0 hours
- cash cost cap: ¥0 (free public data only)

## Target claim (frozen quote)

arXiv:2412.20138 "TradingAgents: Multi-Agents LLM Financial Trading Framework"
(TauricResearch), evaluation window 2024-06-19 to 2024-11-19 (as stated in arXiv HTML v1):

> AAPL: Cumulative Return **26.62%**, Sharpe **8.21**, Max Drawdown 0.91%
> — versus Buy & Hold reported at **−5.23%** for AAPL over the same window.
> GOOGL: Sharpe 6.39. AMZN: Sharpe 5.60.

- Paper: https://arxiv.org/abs/2412.20138 (latest version at registration: **v7**, last
  revised 2025-06-03; the quoted figures are from HTML v1 — the v1→v7 diff is itself a
  secondary observation)
- Code: https://github.com/TauricResearch/TradingAgents
  - stars at registration: 94,741
  - HEAD at registration: `a33fd4c0f134485a43553a2c23a63cb14adbd88f` (2026-07-18)
- Known prior discussion: Issue #203 (look-ahead bias report), arXiv:2605.16895
  ("The Alpha Illusion") — noted as context, not used as evidence.

## Primary kill condition (the only verdict-driving test)

Recompute the buy-and-hold total return of AAPL from **2024-06-19 to 2024-11-19** using
dividend-adjusted daily closes (Yahoo Finance, `AAPL` adjusted close, first available
close on/after start date to last available close on/before end date).

- The paper's comparison rests on B&H = **−5.23%** for AAPL.
- **KILL** if recomputed B&H ≥ **0.0%** (i.e., the stated baseline is off by ≥ 5.23
  percentage points and the headline "beats buy-and-hold" comparison is built on a
  misstated baseline).
- **SURVIVE** if recomputed B&H ≤ −3.0% (baseline materially correct; the comparison
  stands as stated, whatever one thinks of Sharpe 8.21).
- Result in (−3.0%, 0.0%): verdict `REVISE` — baseline imprecise but comparison not
  fully invalidated; report exact figure.
- If the paper's stated window cannot be located unambiguously in the registered arXiv
  version: `UNVERIFIABLE`.

## Secondary observations (reported, never verdict-driving)

1. Implied daily return/volatility consistency of Sharpe 8.21 over ~105 trading days.
2. Overlap of the evaluation window with the knowledge cutoffs of the backbone models
   (gpt-4o-mini / gpt-4o / o1-preview) → memorization / look-ahead exposure.
3. Whether arXiv version history (v1→latest) changed the evaluation window or figures.
4. Transaction cost treatment.

## Verification procedure

1. Pin the arXiv version and quote the exact table (30 min).
2. Compute B&H via yfinance script committed to `verification/01/` (30 min).
3. Run secondary checks (60–90 min).
4. Write result + calibration update (30 min).

## Kill hypothesis (why P(kill) = 0.90)

AAPL rose over Jun–Nov 2024; a −5.23% B&H figure is very likely a data or methodology
error in the baseline, and Sharpe > 8 over 5 months with 0.91% MDD is inconsistent with
any realistic daily-return process for a long-only single-name strategy. Registered
before computing anything.
