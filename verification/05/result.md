# Entry 05 — Verification result

- entry: `/home/trow126/falsify-ledger/entries/05-quantitativo-mean-reversion-sharpe-2.md`
- executed: 2026-07-28
- data: real QQQ daily OHLC, Yahoo Finance chart API, adjusted (adjclose factor
  applied to O/H/L), 1999-03-10 .. 2026-07-27, 6887 rows (`data/qqq_chart.json`).
  Evaluation window after 300-day SMA warmup: 2000-05-16 .. 2026-07-27 (6588 days).
- rules: see `rules-extracted.md` (verbatim extraction + interpretations I1–I8).
- code: `reproduce.py`; full log: `run-log.txt`.

## Primary kill condition (verdict-driving)

Long-QQQ "Dynamic Stop Losses" variant (the variant carrying the frozen claim
Sharpe 2.11 / 13.0% ann / −20.3% MDD), rules exactly as disclosed:

| metric | value |
|---|---|
| **S_g** (gross annualized Sharpe, full daily series) | **0.749** |
| **S_c** (5 bps per side on every entry and exit) | **0.622** |
| gross ann. return / MDD | 8.87% / −21.13% |
| net (5 bps) ann. return / MDD | 7.15% / −22.38% |
| time-in-market / trades | 15.3% / 434 |

Mechanical application of the frozen rule:

- S_c = 0.622 < 1.0 → **KILL**
- (SURVIVE would have required S_c ≥ 1.5 and S_g ≥ 1.6; not met by a wide margin.)

### Verdict: **KILL**

The claim's economic content does not survive even before costs: the reproduced
gross Sharpe on real QQQ data is 0.75, roughly a third of the claimed 2.11. Costs
only worsen it. Truncating at the article's window end (2024-12-31) changes
nothing material: S_g 0.78 / S_c 0.65.

## Why the article shows 2.11 (diagnosis, non-verdict)

1. **Sharpe convention.** Computing Sharpe only over invested days (1009 of 6588)
   yields 1.92 gross / 1.77 net — close to the claimed 2.11. The article's
   headline Sharpe appears to be exposure-adjusted (a nonstandard convention that
   is not comparable to buy-and-hold Sharpe and does not represent the risk of the
   actual equity curve). The frozen entry explicitly relegates exposure-adjusted
   figures to secondary observation #3, so the verdict uses the standard
   full-series convention.
2. **Synthetic pre-1999 data.** The article backtests 1993–2024; QQQ launched
   1999-03. Per the frozen protocol this window difference is documented, not
   penalized.
3. My reproduced MDD (−21.1%) matches the claimed −20.3% closely, and my
   time-in-market (15.3%) matches the article's stated "12–15%" — evidence the
   rule reconstruction is faithful; the divergence is in the Sharpe number, not
   the strategy mechanics.

## Alternative interpretation (documented, non-verdict)

Variant B (entries additionally gated by close > SMA300, i.e. the ledger's
"regime filter" paraphrase): gross Sharpe 0.632 / net 0.539 — also < 1.0, so the
verdict is interpretation-invariant.

## Secondary observations (never verdict-driving)

### 1. ±20% perturbation of the three constants (gross full-series Sharpe)

| constant | −20% | base | +20% |
|---|---|---|---|
| band multiplier (2.0 / 2.5 / 3.0) | 0.760 | 0.749 | 0.797 |
| IBS threshold (0.24 / 0.30 / 0.36) | 0.709 | 0.749 | 0.690 |
| SMA length (240 / 300 / 360) | 0.797 | 0.749 | 0.719 |

Sharpe is flat (0.69–0.80) across all perturbations: the constants are not
fragile, but nothing in the neighborhood comes near 2.11 either. The strategy is
robustly mediocre on real data.

### 2. Sub-period gross Sharpe (primary rules)

| period | Sharpe | ann | MDD |
|---|---|---|---|
| dot-com (2000-06-01..2002-12-31) | 0.596 | 11.04% | −20.46% |
| GFC (2007-10-01..2009-06-30) | 1.089 | 17.95% | −11.65% |
| post-2020 (2020-01-01..2026-07-27) | 0.549 | 6.61% | −15.60% |

### 3. Exposure

Time-in-market 15.3%, 434 round-trip trades over ~26.2 years (≈16.6/yr, mean
hold ≈2.3 days). Invested-days-only Sharpe: 1.92 gross / 1.77 with 5 bps.
Sanity check — original rules (no SMA exit) on real QQQ: gross Sharpe 0.879,
13.83% ann, −24.56% MDD, TIM 19.8% (article claims 1.83 on 1993–2024).

## Files

- `article-snapshot.html`, `article-text.txt` — pinned article
- `rules-extracted.md` — verbatim rules + interpretations
- `data/qqq_chart.json` — raw Yahoo data (gitignored dir)
- `reproduce.py` — reproduction code
- `run-log.txt` — full execution log (primary + sanity checks)
- `result.md` — this file
