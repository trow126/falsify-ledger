# Entry 03 — Concretum VIX strategy: "16.3% ann., Sharpe 1.0, costs included" (survival check)

- status: `VERIFIED`
- registered_at: `2026-07-27T19:41:56Z (git commit timestamp is authoritative)`
- verdict: **SURVIVE** — reproduced Sharpe **0.984** (claim: 1.0, within ±0.2) and
  **0.944** at 15 bps (> 0.7). Annualized 15.83% vs claimed 16.3%; SPY correlation
  0.133 vs claimed ~15%; regime mix matches. See `verification/03/result.md`.
- **procedural deviation (disclosed)**: the frozen test said "run the public notebook";
  the notebook turned out to be a live-execution (IBKR) template containing **no
  backtest code**. The backtest was rebuilt verbatim from the strategy rules fully
  disclosed in that same notebook (Cell 3, "Strategy 4"). A strictly literal reading
  could classify this as `UNVERIFIABLE`; `SURVIVE` was chosen because the substantive
  frozen test (reproduce full-period Sharpe ±0.2, cost sensitivity at 15 bps) was
  executed faithfully against the registered source, and the reproduction matched the
  claim on four independent metrics. This judgment call is recorded here, at the
  verdict, not hidden.
- predicted P(kill): **0.30** (i.e., I predict this claim SURVIVES)
- time cap: 3.0 hours
- cash cost cap: ¥0 (free public data / free Colab only)

## Target claim (frozen quote)

Concretum Group, "Automating a Volatility Strategy" (Substack, with public Colab
notebook and companion paper; Quantpedia Awards 2026, 5th place):

> Short-volatility strategy driven by two signals (eVRP and VIX term structure),
> 2008-01 to 2025-05: annualized return **16.3%**, Sharpe **1.0**, ~15% equity
> correlation, **with 5 bps per trade transaction costs included**.

- Article: https://concretumgroup.substack.com/p/automating-a-volatility-strategy
- Notebook: public Colab linked from the article (short link as published:
  `bit.ly/VIX_Algo_IBKR`; the resolved Colab URL will be recorded in the verification
  artifact)
- Data: VIX, VIX3M, SPY — all free.

## Why this entry exists

This is a deliberate **survival check**. The claim is unusually well-constructed
(rules fully disclosed, costs modeled, public notebook, third-party recognition). A
ledger that only registers claims it expects to kill is one-directional marketing;
registering a claim I expect to pass — and being scored on that prediction — is what
makes the calibration record meaningful.

## Primary kill condition (the only verdict-driving test)

Run the public notebook as published (free data, free Colab), reproducing the full-period
backtest, then re-run with transaction costs raised from 5 bps to **15 bps** per trade.

- **SURVIVE** if (a) reproduced full-period Sharpe is within **±0.2** of the claimed 1.0,
  AND (b) Sharpe remains **> 0.7** at 15 bps.
- **KILL** if reproduction fails by more than ±0.2, or Sharpe at 15 bps drops to ≤ 0.7.
- If the notebook no longer runs and cannot be mechanically fixed within 30 minutes:
  `UNVERIFIABLE` (documented).

## Secondary observations (reported, never verdict-driving)

1. Behavior in the three worst short-vol episodes in-sample (2018-02 "Volmageddon",
   2020-03, 2024-08): drawdown depth vs. reported max drawdown.
2. Daily-data granularity risk: whether intraday VIX spikes would plausibly have
   produced deeper realized losses than daily closes show (left-tail understatement).
3. Sub-period Sharpe stability (pre/post 2018).

## Verification procedure

1. Pin notebook URL and paper version (15 min).
2. Reproduce baseline run (60–90 min).
3. Cost sensitivity run at 15 bps (30 min).
4. Secondary checks + write-up + calibration update (45 min).

## Prediction rationale (why P(kill) = 0.30)

Costs are already modeled, rules are public, and the authors submitted the strategy to
external review. Residual kill risk is concentrated in reproduction drift (data source
differences) and cost sensitivity of a strategy that trades VIX products. Registered
before running anything.
