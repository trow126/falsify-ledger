# The most-starred LLM trading paper claims buy-and-hold lost 5.23%. It actually gained 9.12%.

*Cross-post source for dev.to / Medium. Canonical record:
[falsify-ledger](https://github.com/trow126/falsify-ledger).*

TradingAgents (arXiv:2412.20138, ~94,700 GitHub stars) is probably the most visible
"LLM agents trade stocks" project in existence. Its headline result: a multi-agent LLM
framework earned a **26.62% cumulative return on AAPL with a Sharpe ratio of 8.21**
between 2024-06-19 and 2024-11-19 — while buy-and-hold, the paper says, **lost 5.23%**.

That last number is checkable in one API call. So I checked it — but with a twist: I
**froze the test, the verdict rule, and my predicted outcome in a public git commit
before computing anything.**

## The preregistered test

Registered at commit
[`60e8e2b`](https://github.com/trow126/falsify-ledger/commit/60e8e2b), before any data
was fetched:

> Recompute AAPL buy-and-hold total return over 2024-06-19 → 2024-11-19 using Yahoo
> Finance dividend-adjusted daily closes. **KILL if the result is ≥ 0.0%** (the stated
> −5.23% baseline would then be off by ≥ 5.23 points with the wrong sign).
> Predicted P(kill): 0.90.

## The result

| Series | 2024-06-20 | 2024-11-19 | Buy & hold |
|--------|-----------|-----------|------------|
| Adjusted close | 207.88 | 226.83 | **+9.12%** |
| Raw close (robustness) | 209.68 | 228.28 | +8.87% |

AAPL went **up** roughly nine percent over the paper's own evaluation window. The
baseline is off by ~14.4 percentage points, with the wrong sign. The paper's central
contrast — "buy-and-hold lost money, our agent made 26%" — does not survive contact
with the price series. Verdict: **KILL** ([full record with reproduction
script](https://github.com/trow126/falsify-ledger/blob/main/verification/01/result.md)).

Secondary observations (documented but not part of the verdict): a Sharpe of 8.21 over
~105 trading days with a 0.91% max drawdown implies a near-monotonic equity curve that
is characteristic of evaluation artifacts; the repo's own issue tracker contains a
look-ahead bias report (Issue #203); transaction costs are not modeled.

## Why preregister a five-minute check?

Because post-hoc criticism is cheap and unfalsifiable in the other direction: nobody
can tell whether the critic ran ten tests and published the one that worked. The ledger
publishes the prediction *and* the probability first, then scores itself. Three entries
so far: predictions 0.90 / 0.95 / 0.30, outcomes KILL / KILL / **SURVIVE** — the
survivor being a volatility strategy whose claims reproduced almost exactly
([entry 03](https://github.com/trow126/falsify-ledger/blob/main/entries/03-concretum-vix-strategy.md)).
Mean Brier score: 0.034. A ledger that kills everything is a marketing gimmick; a
calibrated one is a measurement instrument.

Every entry freezes exactly one verdict-driving test before looking, publishes free-data
reproduction scripts, and reports procedural deviations at the verdict — including the
one judgment call we had to make in entry 03.

## If you own a claim

If you are about to commit money or engineering time to a quantitative claim — yours or
a vendor's — and want it stress-tested under the same preregistered discipline first,
[open an issue](https://github.com/trow126/falsify-ledger/issues).

*This is methodological review of public claims. It is not investment advice, and it is
not directed at any individual.*
