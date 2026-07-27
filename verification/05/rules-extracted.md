# Entry 05 — Rules extracted verbatim from the article

Source: https://www.quantitativo.com/p/a-mean-reversion-strategy-with-211
Snapshot: `article-snapshot.html` / plain text `article-text.txt` (fetched 2026-07-28).
Article date: May 20, 2024.

## Original rules (frozen quote from article)

> Compute the **rolling mean of High minus Low** over the **last 25 days**;
> Compute the **IBS indicator**: (Close - Low) / (High - Low);
> Compute a **lower band** as the **rolling High** over the **last 10 days** minus
> 2.5 x the rolling mean of High mins Low (first bullet);
> **Go long** whenever **SPY closes under the lower band** (3rd bullet), and
> **IBS is lower than 0.3**;
> **Close the trade** whenever the **SPY close is higher than yesterday's high**.

(The article then swaps SPY for QQQ: "after trying some instruments, I experimented
with QQQ and got much better results" — 1.83 Sharpe on QQQ, 1993–2024.)

## The headline 2.11-Sharpe variant (= "Improvement 2: Dynamic Stop Losses")

The claimed Sharpe 2.11 / 13.0% ann / −20.3% MDD figures belong to Improvement 2,
which is **long-only QQQ, NO market-regime entry filter** ("I decided to abandon the
market regime filter but improve the exit strategy"), with two exit conditions:

> Close the trade whenever the **price is higher than yesterday's high** (same as before);
> Close the trade whenever the **price is lower than the 300-SMA** (new condition).

So the 300-SMA appears as a **dynamic-stop exit**, not as an entry regime filter
(the ledger entry's paraphrase "300-day SMA regime filter" is a slight mislabel;
the regime-filter experiment is a different variant with Sharpe 2.25 / 7.4% ann).
The SMA length 300 was chosen by trying 150/200/300 ("I found that 300 was the best
option ... I tried 4-5 options only").

## Details NOT disclosed in the article (interpretation required)

- Band multiplier: 2.5 (disclosed). Rolling-high window: 10 days (disclosed) —
  note: the ledger's frozen quote says "25-day average-range band"; the 25 days
  is the average-range window, the band's rolling high uses 10 days.
- Entry price: not stated; rules are close-based → interpreted as entry at the
  signal day's close (I2).
- Whether rolling windows include the current bar: not stated → include (I1).
- Position sizing: not stated → 100% of equity, no leverage (I5).
- Costs/commissions: not modeled (author confirms in comments he was asked
  "have you assumed any commissions?"; headline figures are gross).
- Sharpe convention: not stated. Full daily-series Sharpe (flat days included,
  rf=0) is used for the verdict (I8); an invested-days-only figure is reported
  as documentation because it appears to be closer to the article's convention.
- Data 1993–1999: QQQ launched 1999-03, so the article's 1993 start uses
  synthetic/backfilled data. Reproduction uses real QQQ from inception
  (frozen: documented, not penalized).

All interpretations were mechanical and took well under 30 minutes → not
UNVERIFIABLE.
