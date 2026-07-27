# The most-starred LLM trading paper claims buy-and-hold lost 5.23%. It actually gained 9.12%.

*Cross-post source. Canonical record:
[falsify-ledger](https://github.com/trow126/falsify-ledger).*

TradingAgents (arXiv:2412.20138, ~94,700 GitHub stars) is probably the most visible
"LLM agents trade stocks" project right now. The headline result: a multi-agent LLM
framework earned a 26.62% cumulative return on AAPL with a Sharpe ratio of 8.21 between
2024-06-19 and 2024-11-19, while buy-and-hold supposedly lost 5.23% over the same
window.

That last number takes one API call to check. So I checked it. With a twist: I wrote
down the test, the verdict rule, and my predicted outcome, and committed all of it to a
public repo before touching any data.

## The test I froze

From commit [`60e8e2b`](https://github.com/trow126/falsify-ledger/commit/60e8e2b),
registered before anything was computed:

> Recompute AAPL buy-and-hold total return over 2024-06-19 → 2024-11-19 using Yahoo
> Finance dividend-adjusted daily closes. KILL if the result is ≥ 0.0% — because then
> the stated −5.23% baseline is off by more than five points and has the wrong sign.
> Predicted P(kill): 0.90.

## What came back

| Series | 2024-06-20 | 2024-11-19 | Buy & hold |
|--------|-----------|-----------|------------|
| Adjusted close | 207.88 | 226.83 | **+9.12%** |
| Raw close (robustness) | 209.68 | 228.28 | +8.87% |

AAPL went up about nine percent over the paper's own evaluation window. The reported
baseline is off by roughly 14 percentage points, sign included. Whatever the agent
returned, the paper's central contrast — "buy-and-hold lost money, our agent made 26%"
— is built on a number that the price series contradicts. Verdict: KILL. Full record
and reproduction script are in
[verification/01](https://github.com/trow126/falsify-ledger/blob/main/verification/01/result.md).

A few things I noted but kept out of the verdict: a Sharpe of 8.21 over ~105 trading
days with a 0.91% max drawdown implies an equity curve that barely ever dips, which in
a single-name equity strategy usually points to an evaluation artifact rather than
alpha. The repo's own issue tracker has a look-ahead bias report (Issue #203). Costs
aren't modeled.

## Why bother preregistering a five-minute check?

Because post-hoc criticism is cheap. Nobody can tell whether a critic ran ten tests and
published the one that landed. Writing the prediction down first — with a probability
attached — makes the critic auditable too.

I keep these in a public ledger. Five entries so far, each with the verdict rule
committed before the data was touched. Predictions: 0.90 / 0.95 / 0.30 / 0.85 / 0.70.
Outcomes: KILL / KILL / SURVIVE / SURVIVE / KILL. The survivors are real: entry 03 was
a volatility strategy I expected to pass, and it reproduced almost exactly
([entry](https://github.com/trow126/falsify-ledger/blob/main/entries/03-concretum-vix-strategy.md)).
Entry 04 survived its frozen test on a technicality in my own cost wording, and the
entry says so right at the verdict, along with the reading under which it would have
failed. Misses cost me Brier score, publicly.

## If you own a claim

If you're about to commit money or engineering time to a quantitative claim — yours or
a vendor's — and want it tested this way first,
[open an issue](https://github.com/trow126/falsify-ledger/issues). The verdict rule
gets frozen before either of us sees the result.

*This is methodological review of public claims. It is not investment advice, and it is
not directed at any individual.*
