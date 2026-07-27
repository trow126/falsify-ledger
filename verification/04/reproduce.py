#!/usr/bin/env python
"""Entry 04 verification: QuantReturns "Overnight Mean-Reversion" (CO-OC) on ARKG/XBI/IBB.

Reproduces the article's CO-OC cross-sectional reversal strategy and applies the
frozen kill condition from entries/04-quantreturns-overnight-sharpe-4.md.

Rules as disclosed (article, Oct 3 2025):
  - Formation: overnight return CO_i(t) = Open_i(t)/Close_i(t-1) - 1
  - Cross-sectionally demean CO across the universe (ARKG, XBI, IBB)
  - Linear signal -> weight mapping, REVERSAL sign (long low overnight, short high)
  - Scale so longs = +100% and shorts = -100% of portfolio value (gross 200%)
  - Hold during the same day's intraday session: P&L_i = OC_i(t) = Close_i(t)/Open_i(t) - 1
  - Winsorize formation returns two-sided (level undisclosed; we use 1%/99%,
    sensitivity at no-winsorization and 5%/95%)
  - Sample: article backtest window 2007-01-01 .. 2025-09-01

Data: Yahoo Finance via yfinance, auto_adjust=True so Open and Close are adjusted
by the same per-day factor -> both CO and OC ratios are split/dividend consistent.

Costs (frozen entry): 5 bps per side, "10 bps per round trip per day" deducted.
Primary (literal, lenient) reading: flat 0.0010 deduction from the daily strategy
return. Sensitivity: per-notional reading (gross 200% traded in AND out = 400%
notional x 5bps = 20 bps/day).
"""
import numpy as np
import pandas as pd
import yfinance as yf
import sys, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
TICKERS = ["ARKG", "XBI", "IBB"]
START, END = "2006-12-01", "2025-09-02"  # pad start for prior close
SAMPLE_START, SAMPLE_END = "2007-01-01", "2025-09-01"
ANN = np.sqrt(252)

def load():
    cache = os.path.join(HERE, "data", "prices_adj.pkl")
    if os.path.exists(cache):
        return pd.read_pickle(cache)
    df = yf.download(TICKERS, start=START, end=END, auto_adjust=True, progress=False)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    df.to_pickle(cache)
    return df

def build_returns(px):
    o = px["Open"]; c = px["Close"]
    co = o / c.shift(1) - 1.0          # overnight (formation)
    oc = c / o - 1.0                   # intraday (holding)
    m = (co.index >= SAMPLE_START) & (co.index <= SAMPLE_END)
    return co.loc[m], oc.loc[m]

def winsorize(df, lo, hi):
    if lo is None:
        return df
    out = df.copy()
    for col in out:
        s = out[col].dropna()
        ql, qh = s.quantile(lo), s.quantile(hi)
        out[col] = out[col].clip(ql, qh)
    return out

def strategy_returns(co, oc, wlo=0.01, whi=0.99):
    cow = winsorize(co, wlo, whi)
    sig = -(cow.sub(cow.mean(axis=1), axis=0))        # demean, reversal sign
    valid = cow.notna().sum(axis=1) >= 2
    gross_abs = sig.abs().sum(axis=1)
    w = sig.div(gross_abs, axis=0) * 2.0              # gross 200% (100 long/100 short)
    w[~valid] = np.nan
    ret = (w * oc).sum(axis=1, min_count=1)
    return ret.dropna(), w

def stats(r):
    mu, sd = r.mean(), r.std(ddof=1)
    sharpe = mu / sd * ANN
    t = mu / sd * np.sqrt(len(r))
    return dict(n=len(r), mean_daily=mu, std_daily=sd, sharpe_ann=sharpe, tstat=t)

def main():
    px = load()
    co, oc = build_returns(px)
    r, w = strategy_returns(co, oc)
    r.to_csv(os.path.join(HERE, "data", "strategy_daily_returns.csv"))

    sg = stats(r)
    print("=== Gross (no costs), winsorize 1%/99%, 2007-01-01..2025-09-01 ===")
    print(json.dumps(sg, indent=2))

    # Costs
    r_flat10 = r - 0.0010     # frozen literal: 10 bps round trip per day
    r_pn20   = r - 0.0020     # per-notional: 400% traded notional x 5bps
    sc = stats(r_flat10)
    sc20 = stats(r_pn20)
    print("\n=== Net, flat 10 bps/day (VERDICT-DRIVING S_c) ===")
    print(json.dumps(sc, indent=2))
    print("\n=== Net, 20 bps/day (per-notional sensitivity) ===")
    print(json.dumps(sc20, indent=2))

    # Winsorization sensitivity
    for tag, (lo, hi) in {"none": (None, None), "5/95": (0.05, 0.95)}.items():
        rr, _ = strategy_returns(co, oc, lo, hi)
        print(f"\n--- Winsorize {tag}: gross Sharpe = {stats(rr)['sharpe_ann']:.3f}, "
              f"net10 Sharpe = {stats(rr - 0.0010)['sharpe_ann']:.3f}")

    # Secondary 1: break-even daily cost where net Sharpe crosses 1.0
    # Sharpe(r - c) = 1/sqrt(252) per day => c = mean - std/sqrt(252)... solve directly
    c_be_1 = r.mean() - r.std(ddof=1) / ANN     # daily cost s.t. Sharpe = 1.0
    c_be_2 = r.mean() - 2 * r.std(ddof=1) / ANN # Sharpe = 2.0
    c_be_0 = r.mean()                           # Sharpe = 0
    print(f"\n=== Secondary: break-even daily cost ===")
    print(f"daily cost for net Sharpe=2.0: {c_be_2*1e4:.2f} bps/day")
    print(f"daily cost for net Sharpe=1.0: {c_be_1*1e4:.2f} bps/day")
    print(f"daily cost for net Sharpe=0.0: {c_be_0*1e4:.2f} bps/day")
    print(f"(per-side bps equivalent at gross 200%: divide daily bps by 4)")

    # Secondary 2: sub-period stability
    mid = r.index[len(r) // 2]
    h1, h2 = r.loc[:mid], r.loc[mid:][1:]
    print(f"\n=== Secondary: sub-periods (gross) ===")
    print(f"H1 {h1.index[0].date()}..{h1.index[-1].date()}: Sharpe {stats(h1)['sharpe_ann']:.3f}  mean {h1.mean()*1e4:.1f} bps/d")
    print(f"H2 {h2.index[0].date()}..{h2.index[-1].date()}: Sharpe {stats(h2)['sharpe_ann']:.3f}  mean {h2.mean()*1e4:.1f} bps/d")
    # net 10bps sub-periods
    print(f"H1 net10 Sharpe {stats(h1-0.001)['sharpe_ann']:.3f} | H2 net10 Sharpe {stats(h2-0.001)['sharpe_ann']:.3f}")

    # Data coverage note
    first_valid = {t: str(co[t].first_valid_index().date()) for t in TICKERS}
    print(f"\nFirst valid overnight-return date per ticker: {first_valid}")
    n2 = int((co.notna().sum(axis=1) == 2).sum()); n3 = int((co.notna().sum(axis=1) == 3).sum())
    print(f"Days with 2 assets: {n2}, with 3 assets: {n3}")

    # Verdict (frozen)
    S_g, S_c = sg["sharpe_ann"], sc["sharpe_ann"]
    if S_c < 2.0:
        verdict = "KILL"
    elif S_c >= 2.0 and S_g >= 3.44:
        verdict = "SURVIVE"
    else:
        verdict = "REVISE"
    print(f"\n=== FROZEN VERDICT ===\nS_g = {S_g:.3f}   S_c = {S_c:.3f}   ->  {verdict}")

if __name__ == "__main__":
    main()
