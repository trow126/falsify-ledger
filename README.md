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
| 05 | Quantitativo — "Mean reversion with a 2.11 Sharpe" | 2026-07-27 | **KILL** | 0.70 | Full-series Sharpe is 0.75 gross / 0.62 net, not 2.11 — the claim reflects an invested-days-only convention ([result](verification/05/result.md)) |

Calibration after 5 entries: predictions 0.90 / 0.95 / 0.30 / 0.85 / 0.70 vs outcomes
KILL / KILL / SURVIVE / SURVIVE* / KILL — mean Brier score **0.183** (0 = perfect,
0.25 = uninformed). The 0.85-miss on entry 04 came from ambiguous cost-basis wording in
our own frozen test; the flip condition is disclosed at that entry's verdict, and later
entries specify the cost basis explicitly.

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

## Paid verification (open offer)

The entries above were free public work. The same discipline is available for your own
decisions, as a paid engagement:

- Scope: one claim about a non-financial software, AI, or data project — a vendor's
  accuracy number, a build-vs-buy assumption, a performance claim you're about to
  commit money or engineering time to.
- What you get: the claim and verdict criteria frozen in writing before results, up to
  three minimal falsification tests, and a kill / revise / proceed memo within seven
  days. Reproducible evidence either way.
- Price: fixed fee, deposit from ¥50,000 (~$350). No success fee — I get paid the same
  whether your claim survives or dies, so I have no reason to manufacture problems.
- Not offered: financial product selection, trading advice, strategy parameters.
  Your data stays private; nothing enters this public ledger without written consent.

To start, [open an issue](https://github.com/trow126/falsify-ledger/issues) titled
"Kill Sprint request" with one sentence about the claim. First response within 48 hours.

## Contact

Questions, or a public claim you'd like to see verified for free in the ledger:
also via [issues](https://github.com/trow126/falsify-ledger/issues).

---

*Maintained as part of a 30-day preregistered experiment; the measurement rules
(what counts as evidence, payment, and success) were frozen on 2026-07-28 before any
result was observed.*
