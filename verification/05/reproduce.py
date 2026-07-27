#!/usr/bin/env python3
"""Entry 05 verification: Quantitativo "A mean reversion strategy with 2.11 Sharpe".

Reproduces the long-QQQ "Dynamic Stop Losses" variant (Improvement 2, the variant
carrying the frozen headline claim: Sharpe 2.11 / 13.0% ann / -20.3% MDD) on real
QQQ data (Yahoo adjusted OHLC, inception 1999-03 onward).

Rules as disclosed in the article (verbatim extraction in rules-extracted.md):
  ADR25   = rolling mean of (High - Low) over last 25 days
  IBS     = (Close - Low) / (High - Low)
  band    = rolling max of High over last 10 days - 2.5 * ADR25
  ENTRY   : close < band AND IBS < 0.3           (enter at that day's close)
  EXIT    : close > yesterday's high  OR  close < 300-day SMA of close
            (exit at that day's close; checked from the day after entry)

Interpretations (documented, each < 30 min mechanical choice):
  I1: rolling windows include the current day (pandas default).
  I2: entry/exit executed at the same day's close as the signal (article gives
      close-based rules; no next-open language).
  I3: exit checked starting the day AFTER entry (cannot enter and exit on the
      same close).
  I4: no same-day re-entry after an exit.
  I5: position sizing = 100% of equity per trade, no leverage.
  I6: Improvement 2 explicitly "abandons the market regime filter", so entries
      are NOT gated by the 300-SMA (variant A, primary). Variant B (entries
      additionally require close > SMA300, matching the ledger's paraphrase
      "regime filter") is computed as a documented alternative only.
  I7: Yahoo auto-adjusted OHLC: O/H/L scaled by adjclose/close.
  I8: Sharpe = mean/std * sqrt(252) of daily strategy returns over all trading
      days in the evaluation window (flat days included, rf=0), matching the
      convention that makes the article's own buy-and-hold numbers comparable.
Costs: S_c deducts 5 bps of equity on each entry day and each exit day.
"""
import json
import math
import numpy as np
import pandas as pd

DATA = "/home/trow126/falsify-ledger/verification/05/data/qqq_chart.json"


def load_qqq():
    raw = json.load(open(DATA))["chart"]["result"][0]
    q = raw["indicators"]["quote"][0]
    adj = raw["indicators"]["adjclose"][0]["adjclose"]
    df = pd.DataFrame({
        "open": q["open"], "high": q["high"], "low": q["low"],
        "close": q["close"], "adjclose": adj,
    }, index=pd.to_datetime(raw["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None))
    df = df.dropna()
    f = df["adjclose"] / df["close"]
    out = pd.DataFrame({
        "high": df["high"] * f, "low": df["low"] * f, "close": df["adjclose"],
    })
    return out


def build_signals(df, mult=2.5, ibs_max=0.3, sma_n=300, entry_gate_sma=False):
    h, l, c = df["high"], df["low"], df["close"]
    adr = (h - l).rolling(25).mean()
    band = h.rolling(10).max() - mult * adr
    ibs = (c - l) / (h - l)
    sma = c.rolling(sma_n).mean()
    entry = (c < band) & (ibs < ibs_max)
    if entry_gate_sma:
        entry = entry & (c > sma)
    exit_ = (c > h.shift(1)) | (c < sma)
    return entry, exit_, sma


def backtest(df, entry, exit_, cost_per_side=0.0):
    c = df["close"].values
    ret = np.zeros(len(c))
    ret[1:] = c[1:] / c[:-1] - 1.0
    ent = entry.values
    exi = exit_.values
    pos_overnight = np.zeros(len(c))  # position held from close t-1 into day t
    strat = np.zeros(len(c))
    in_pos = False
    entry_day = -1
    n_trades = 0
    for t in range(len(c)):
        held = 1.0 if in_pos else 0.0
        strat[t] = held * ret[t]
        pos_overnight[t] = held
        exited_today = False
        if in_pos and t > entry_day and exi[t]:
            in_pos = False
            exited_today = True
            strat[t] -= cost_per_side  # exit cost at close t
        # I4: no same-day re-entry after an exit on the same close
        if not in_pos and not exited_today and ent[t]:
            in_pos = True
            entry_day = t
            n_trades += 1
            strat[t] -= cost_per_side  # entry cost at close t
    return pd.Series(strat, index=df.index), n_trades, pd.Series(pos_overnight, index=df.index)


def stats(sr, tim=None):
    n = len(sr)
    if n == 0 or sr.std(ddof=1) == 0:
        return dict(sharpe=float("nan"), ann=float("nan"), mdd=float("nan"), n=n)
    sharpe = sr.mean() / sr.std(ddof=1) * math.sqrt(252)
    eq = (1 + sr).cumprod()
    ann = eq.iloc[-1] ** (252 / n) - 1
    mdd = (eq / eq.cummax() - 1).min()
    return dict(sharpe=sharpe, ann=ann, mdd=mdd, n=n)


def run(df, label, mult=2.5, ibs_max=0.3, sma_n=300, entry_gate_sma=False, cost=0.0, start=None, end=None):
    entry, exit_, _ = build_signals(df, mult, ibs_max, sma_n, entry_gate_sma)
    # warmup: evaluate from first index where SMA is defined
    valid = df.index[max(sma_n, 25, 10) - 1:]
    strat, n_trades, pos = backtest(df, entry, exit_, cost)
    strat = strat.loc[valid[0]:]
    pos = pos.loc[valid[0]:]
    if start:
        strat = strat.loc[start:]
        pos = pos.loc[start:]
    if end:
        strat = strat.loc[:end]
        pos = pos.loc[:end]
    s = stats(strat)
    tim = pos.mean()
    return dict(label=label, **s, tim=tim, trades=n_trades)


def fmt(r):
    return (f"{r['label']:<58} Sharpe={r['sharpe']:6.3f}  Ann={r['ann']*100:6.2f}%  "
            f"MDD={r['mdd']*100:6.2f}%  TIM={r['tim']*100:5.1f}%  trades={r['trades']:4d}  days={r['n']}")


def main():
    df = load_qqq()
    print(f"QQQ rows: {len(df)}  span: {df.index[0].date()} .. {df.index[-1].date()}")

    print("\n=== PRIMARY (verdict-driving) — variant A: article rules, dynamic stop, no entry gate ===")
    g = run(df, "S_g  gross (no costs)")
    c5 = run(df, "S_c  5 bps per side on entry and exit", cost=0.0005)
    print(fmt(g))
    print(fmt(c5))
    S_g, S_c = g["sharpe"], c5["sharpe"]
    if S_c < 1.0:
        verdict = "KILL"
    elif S_c >= 1.5 and S_g >= 1.6:
        verdict = "SURVIVE"
    else:
        verdict = "REVISE"
    print(f"\nS_g = {S_g:.3f}   S_c = {S_c:.3f}   ->  VERDICT: {verdict}")

    print("\n=== Alternative interpretation (documented only, not verdict-driving) ===")
    print(fmt(run(df, "variant B: entry also gated by close > SMA300 (gross)", entry_gate_sma=True)))
    print(fmt(run(df, "variant B: entry also gated by close > SMA300 (5bps)", entry_gate_sma=True, cost=0.0005)))

    print("\n=== SECONDARY 1: +/-20% perturbation of the three constants (gross Sharpe) ===")
    for mult in (2.0, 2.5, 3.0):
        print(fmt(run(df, f"band multiplier = {mult}", mult=mult)))
    for ibs in (0.24, 0.3, 0.36):
        print(fmt(run(df, f"IBS threshold   = {ibs}", ibs_max=ibs)))
    for sma in (240, 300, 360):
        print(fmt(run(df, f"SMA length      = {sma}", sma_n=sma)))

    print("\n=== SECONDARY 2: sub-period Sharpe (gross, primary rules) ===")
    print(fmt(run(df, "dot-com   (2000-06-01 .. 2002-12-31)", start="2000-06-01", end="2002-12-31")))
    print(fmt(run(df, "GFC       (2007-10-01 .. 2009-06-30)", start="2007-10-01", end="2009-06-30")))
    print(fmt(run(df, "post-2020 (2020-01-01 .. end)", start="2020-01-01")))

    print("\n=== SECONDARY 3: exposure / trades (in primary rows above: TIM, trades) ===")
    print("(time-in-market and trade count reported per row)")


if __name__ == "__main__":
    main()
