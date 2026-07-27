# Falsify Ledger — Public Kill Ledger

A public, preregistered falsification record of quantitative AI / backtest claims.

## What this is

For each target claim, I **freeze a verdict prediction and a verification procedure
before looking at the result**, commit it to this repository (the git timestamp is the
preregistration evidence), then run the verification and publish the outcome — including
when my prediction was wrong. Every entry is scored on calibration (Brier score), so the
ledger accumulates a verifiable track record of judging other people's claims, not a
highlight reel.

- 1 ledger entry = 1 preregistration + 1 published verification result. Preregistrations
  without published results do not count.
- Verdicts are one of `KILL` (the claim as stated is invalidated by the frozen test),
  `SURVIVE` (the claim passes the frozen test), `UNVERIFIABLE` (the frozen test cannot
  be executed from public artifacts — itself a documented finding).
- Each entry freezes exactly **one primary kill condition**. Secondary observations are
  reported but never drive the verdict.
- Amendments after registration keep the original text and add a dated correction. No
  silent edits.

## Why

Backtest and AI-performance claims routinely fail under leakage checks, cost injection,
baseline recomputation, and window shifts. Sellers rarely run these tests on their own
claims; buyers rarely know how cheap the tests are. This ledger demonstrates the tests —
and the discipline of preregistering the judgment — in public.

This is methodological review of published, public claims. It is not investment advice,
not a recommendation to buy or sell anything, and not directed at any private individual.

## Entries

| # | Target | Registered | Verdict | Predicted P(kill) | Result |
|---|--------|-----------|---------|-------------------|--------|
| 01 | TradingAgents (arXiv:2412.20138) — "Sharpe 8.21 on AAPL" | 2026-07-27 | **KILL** | 0.90 | B&H baseline is +9.12%, not −5.23% ([result](verification/01/result.md)) |
| 02 | Qiita LSTM stock prediction (172 LGTM) — high-accuracy claim | 2026-07-27 | **KILL** | 0.95 | Naive lag-1 RMSE beats the LSTM by 42% ([result](verification/02/result.md)) |
| 03 | Concretum VIX strategy — "16.3% ann., Sharpe 1.0, costs included" | 2026-07-27 | **SURVIVE** | 0.30 | Reproduced Sharpe 0.984; 0.944 at 15 bps ([result](verification/03/result.md)) |
| 04 | QuantReturns — "Overnight mean-reversion, Sharpe 4.44" | 2026-07-27 | **SURVIVE*** | 0.85 | Gross reproduces (4.18); survives the literal frozen cost test (2.75), but flips to KILL under a per-notional cost reading — ambiguity disclosed at the verdict ([result](verification/04/result.md)) |
| 05 | Quantitativo — "Mean reversion with a 2.11 Sharpe" | 2026-07-27 | — | 0.70 | — |

Calibration after 3 entries: predictions 0.90 / 0.95 / 0.30 vs outcomes KILL / KILL /
SURVIVE — mean Brier score **0.034** (0 = perfect, 0.25 = uninformed).

Entry 03 is deliberately a **survival-check candidate**: a claim I expect to pass. A
ledger that kills everything is a marketing gimmick; a calibrated one is a measurement
instrument.

## Method summary

1. Select a public, quantitative, third-party-verifiable claim.
2. Freeze: exact claim quote, source (URL / arXiv version / commit SHA), one primary
   kill condition, verification procedure, time cap, and P(kill).
3. Commit the frozen entry (registration timestamp = commit time).
4. Run the verification within the time cap, at zero cash cost, on free public data.
5. Publish the result, the reproduction artifact (script/notebook), and the calibration
   update — regardless of outcome.

## Contact

If you own a claim or a purchase/build decision and want it stress-tested under the same
preregistered discipline before you commit to it: **open an issue on this repository.**

---

*Maintained as part of a 30-day preregistered experiment; the measurement rules
(what counts as evidence, payment, and success) were frozen on 2026-07-28 before any
result was observed.*
