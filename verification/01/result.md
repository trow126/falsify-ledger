# Entry 01 — Verification result

- executed_at: 2026-07-27T19:47Z (registration commit: `60e8e2b`, 2026-07-27T19:41:56Z)
- time spent: ~0.5 h (well under the 3.0 h cap)
- cash cost: ¥0

## Primary kill condition result

Frozen test: recompute AAPL buy-and-hold total return, 2024-06-19 → 2024-11-19,
Yahoo Finance dividend-adjusted daily closes. KILL if ≥ 0.0%.

| Series | First close (on/after 2024-06-19) | Last close (on/before 2024-11-19) | B&H |
|--------|------------------------------------|-----------------------------------|-----|
| Adjusted close (frozen source) | 2024-06-20: 207.88 | 2024-11-19: 226.83 | **+9.12%** |
| Raw close (robustness check) | 2024-06-20: 209.68 | 2024-11-19: 228.28 | +8.87% |

Note: 2024-06-19 was a US market holiday (Juneteenth); the first available close is
2024-06-20, exactly as the frozen procedure specifies.

**Recomputed B&H = +9.12% ≥ 0.0% → verdict: KILL.**

The paper's stated baseline (−5.23%) is off by ≈ **14.4 percentage points** and has the
wrong sign. The headline comparison "26.62% cumulative return vs. buy-and-hold −5.23%"
is built on a misstated baseline: against the actual +9.12% B&H, the claimed strategy
return would still be higher, but the framing "buy-and-hold lost money, the agent made
26%" — the paper's central marketing contrast — does not survive contact with the price
series. Per the frozen rubric, the verdict applies to the comparison claim as registered.

## Secondary observations (not verdict-driving)

1. **Sharpe 8.21 plausibility**: 26.62% over ~105 trading days with max drawdown 0.91%
   implies a daily return/vol profile (≈0.23%/day mean against ≈0.44%/day vol) with
   near-monotonic equity growth in a single-name equity strategy — a profile
   characteristic of look-ahead or evaluation artifacts rather than tradable alpha.
2. **Look-ahead exposure**: the repository's own issue tracker contains a look-ahead
   bias report (Issue #203: data retrieval during backtest can access information after
   the decision date). Not independently re-executed here (documented limitation).
3. **arXiv version drift**: the paper is at v7 (last revised 2025-06-03); the quoted
   figures are from HTML v1. A full v1→v7 diff of the evaluation section was NOT
   performed within the time cap — documented as unaudited.
4. Transaction costs are not modeled in the quoted results.

## Calibration update

- Predicted P(kill): 0.90 → outcome: KILL.
- Brier contribution: (1 − 0.90)² = **0.01**.
