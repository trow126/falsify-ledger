#!/usr/bin/env python3
"""Reproduction backtest for Concretum "Automating a Volatility Strategy"
(falsify-ledger entry 03).

Strategy rules taken verbatim from the public notebook (Cell 3, "Strategy 4"):
  eRV30 = std(last 10 SPY daily returns, ddof=1) * sqrt(252) * 100
  eVRP  = VIX_close - eRV30
  cond1: eVRP > 0  and VIX < VIX3M -> short vol, exposure = -VIX/100
  cond2: eVRP <= 0 and VIX < VIX3M -> short vol, exposure = -0.5 * VIX/100
  cond3: eVRP <= 0 and VIX > VIX3M -> long vol,  exposure = +VIX/100
  cond4: eVRP > 0  and VIX > VIX3M -> cash
  Rebalance only when |target - current| weight drift > 2% (notebook default
  tolerance). Signal at the close of day t, executed MOC at the same close,
  so the position earns day t+1's return.

Traded instrument: 30-day constant-maturity short-term VIX futures excess
return index (SPVXSP-style), built from free CBOE daily settles. This is the
-1x/-0.5x/+1x underlier of XIV/SVXY/VXX. Costs: cost_bps * |traded exposure|.
"""
import datetime as dt
import glob
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

START = "2008-01-01"
END = "2025-05-31"
TOLERANCE = 0.02  # notebook default weight tolerance (2%)


# ---------------------------------------------------------------- data loading
def load_cboe_index(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().upper() for c in df.columns]
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df.set_index("DATE")["CLOSE"].sort_index()


def load_yahoo_close(path):
    df = pd.read_csv(path, skiprows=3, header=None)
    ncol = df.shape[1]
    cols = ["Date", "AdjClose", "Close", "High", "Low", "Open", "Volume"][:ncol]
    df.columns = cols
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date")["AdjClose"].astype(float).sort_index()


def load_contracts():
    """Return dict: expiry_date -> Series(settle by trade date)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(DATA, "vx", "VX_*.csv"))):
        df = pd.read_csv(path)
        df.columns = [c.strip() for c in df.columns]
        df["Trade Date"] = pd.to_datetime(df["Trade Date"], format="mixed")
        s = df.set_index("Trade Date")["Settle"].astype(float)
        s = s[s > 0].sort_index()
        if len(s) < 10:
            continue
        expiry = s.index[-1] + pd.Timedelta(days=1)  # last trading day + 1
        out[expiry] = s
    return out


def build_st_futures_index(contracts, calendar):
    """SPVXSP-style 30d constant maturity excess-return index (daily)."""
    expiries = sorted(contracts.keys())
    # roll date per contract: its last trading day (business day before expiry)
    last_td = {e: contracts[e].index[-1] for e in expiries}
    cal = pd.DatetimeIndex(calendar)
    pos = {d: i for i, d in enumerate(cal)}

    rets = pd.Series(index=cal, dtype=float)
    prev = None  # (m1, m2, w1, w2, F1, F2)
    for d in cal:
        nxt = [e for e in expiries if last_td[e] >= d]
        if len(nxt) < 2:
            continue
        m1, m2 = nxt[0], nxt[1]
        roll1 = last_td[m1]
        idx1 = [e for e in expiries if last_td[e] < d]
        if idx1:
            roll0 = last_td[idx1[-1]]
            dt_total = pos.get(roll1, None), pos.get(roll0, None)
        else:
            dt_total = (None, None)
        if roll1 in pos and idx1 and last_td[idx1[-1]] in pos:
            total_bd = pos[roll1] - pos[last_td[idx1[-1]]]
            rem_bd = pos[roll1] - pos[d]
            w1 = max(0.0, min(1.0, rem_bd / total_bd)) if total_bd > 0 else 0.0
        else:
            w1 = 0.5
        w2 = 1.0 - w1
        f1 = contracts[m1].reindex([d]).iloc[0] if d in contracts[m1].index else np.nan
        f2 = contracts[m2].reindex([d]).iloc[0] if d in contracts[m2].index else np.nan
        if prev is not None:
            pm1, pm2, pw1, pw2, pf1, pf2 = prev
            # today's prices of yesterday's contracts
            c1 = contracts[pm1]
            c2 = contracts[pm2]
            t1 = c1[c1.index <= d].iloc[-1] if (c1.index <= d).any() else np.nan
            t2 = c2[c2.index <= d].iloc[-1] if (c2.index <= d).any() else np.nan
            denom = pw1 * pf1 + pw2 * pf2
            if denom and not np.isnan(denom) and not (np.isnan(t1) or np.isnan(t2)):
                rets[d] = (pw1 * (t1 - pf1) + pw2 * (t2 - pf2)) / denom
        if not (np.isnan(f1) or np.isnan(f2)):
            prev = (m1, m2, w1, w2, f1, f2)
    return rets.dropna()


# ------------------------------------------------------------------- strategy
def run_strategy(df, cost_bps, tolerance=TOLERANCE):
    """df: columns spy, vix, vix3m, idx_ret (all aligned daily closes).
    Returns daily strategy return series (cost-adjusted)."""
    spy_ret = df["spy"].pct_change()
    erv = spy_ret.rolling(10).std(ddof=1) * np.sqrt(252) * 100
    evrp = df["vix"] - erv
    contango = df["vix"] < df["vix3m"]
    backward = df["vix"] > df["vix3m"]

    target = pd.Series(0.0, index=df.index)
    target[(evrp > 0) & contango] = -df["vix"] / 100.0
    target[(evrp <= 0) & contango] = -0.5 * df["vix"] / 100.0
    target[(evrp <= 0) & backward] = df["vix"] / 100.0
    target[erv.isna()] = 0.0

    dates = df.index
    n = len(dates)
    w = 0.0                      # exposure held during day t (set at close t-1)
    strat = np.zeros(n)
    turnover = np.zeros(n)
    weights = np.zeros(n)
    cost = cost_bps / 1e4
    for t in range(1, n):
        r_idx = df["idx_ret"].iloc[t]
        r_port = w * r_idx
        strat[t] = r_port
        # drifted weight after day t's move
        w_drift = w * (1 + r_idx) / (1 + r_port) if (1 + r_port) != 0 else w
        tgt = target.iloc[t]
        if np.isnan(tgt):
            tgt = w_drift
        if abs(tgt - w_drift) > tolerance:
            turnover[t] = abs(tgt - w_drift)
            strat[t] -= turnover[t] * cost
            w = tgt
        else:
            w = w_drift
        weights[t] = w
    out = pd.DataFrame({"ret": strat, "weight": weights, "turnover": turnover,
                        "target": target, "evrp": evrp, "idx_ret": df["idx_ret"]},
                       index=dates)
    return out


def stats(r, name):
    r = r.dropna()
    ann = (1 + r).prod() ** (252 / len(r)) - 1
    vol = r.std(ddof=1) * np.sqrt(252)
    sharpe = r.mean() / r.std(ddof=1) * np.sqrt(252)
    eq = (1 + r).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    print(f"{name}: N={len(r)} annRet={ann*100:6.2f}%  vol={vol*100:5.2f}%  "
          f"Sharpe={sharpe:5.3f}  maxDD={dd*100:6.2f}%")
    return {"ann": ann, "vol": vol, "sharpe": sharpe, "maxdd": dd, "eq": eq}


def episode_dd(r, start, end):
    r = r.loc[start:end]
    eq = (1 + r).cumprod()
    return (eq / eq.cummax() - 1).min()


def main():
    vix = load_cboe_index(os.path.join(DATA, "VIX_History.csv"))
    vix3m_cboe = load_cboe_index(os.path.join(DATA, "VIX3M_History.csv"))
    vix3m_y = load_yahoo_close(os.path.join(DATA, "VIX3M_yahoo.csv"))
    spy = load_yahoo_close(os.path.join(DATA, "SPY.csv"))

    # VIX3M: CBOE official where available (2009-09+), Yahoo backfill before
    vix3m = vix3m_cboe.combine_first(vix3m_y)
    ovl = pd.concat([vix3m_cboe, vix3m_y], axis=1, keys=["c", "y"]).dropna()
    print(f"VIX3M CBOE-vs-Yahoo overlap: n={len(ovl)} "
          f"max|diff|={float((ovl['c']-ovl['y']).abs().max()):.4f}")

    contracts = load_contracts()
    print(f"Loaded {len(contracts)} VX contracts "
          f"({min(contracts).date()} .. {max(contracts).date()})")
    calendar = vix.loc["2007-11-01":END].index
    idx_ret = build_st_futures_index(contracts, calendar)
    ann_decay = (1 + idx_ret).prod() ** (252 / len(idx_ret)) - 1
    print(f"ST futures index: N={len(idx_ret)} annualized drift={ann_decay*100:.1f}%")

    df = pd.concat({"spy": spy, "vix": vix, "vix3m": vix3m, "idx_ret": idx_ret},
                   axis=1)
    df = df.loc["2007-11-01":END]
    df = df.dropna(subset=["idx_ret"])
    df[["spy", "vix", "vix3m"]] = df[["spy", "vix", "vix3m"]].ffill()
    df = df.dropna()

    full = df.loc[START:END]
    print(f"\nBacktest rows {full.index[0].date()} .. {full.index[-1].date()}"
          f" (signals warm up from {df.index[0].date()})")

    res = {}
    for bps in (5, 15):
        out = run_strategy(df, bps)
        r = out.loc[START:END, "ret"]
        res[bps] = stats(r, f"cost={bps:2d}bps")
        res[bps]["r"] = r
        res[bps]["out"] = out

    r5 = res[5]["r"]
    out5 = res[5]["out"].loc[START:END]
    tgt = out5["target"]
    n = len(tgt)
    print(f"\nRegime mix (target): short={100*(tgt<0).sum()/n:.1f}%  "
          f"cash={100*(tgt==0).sum()/n:.1f}%  long={100*(tgt>0).sum()/n:.1f}%")
    print(f"Avg daily one-way turnover (5bps run): "
          f"{out5['turnover'].mean()*100:.2f}% of NAV; "
          f"trades on {100*(out5['turnover']>0).mean():.1f}% of days")

    print("\n--- Secondary observations (not verdict-driving) ---")
    for label, a, b in [("2018-02 Volmageddon", "2018-01-01", "2018-03-31"),
                        ("2020-03 Covid", "2020-02-01", "2020-04-30"),
                        ("2024-08 yen-carry", "2024-07-01", "2024-09-30")]:
        print(f"{label}: episode DD = {episode_dd(r5, a, b)*100:6.2f}%")
    stats(r5.loc[:"2017-12-31"], "sub-period 2008-2017")
    stats(r5.loc["2018-01-01":], "sub-period 2018-2025")

    # equity correlation
    spy_ret = full["spy"].pct_change()
    corr = r5.corr(spy_ret.loc[r5.index])
    print(f"Equity (SPY) correlation: {corr:.3f}")

    # left-tail granularity: worst intraday VIX spike vs close on short days
    vixh = pd.read_csv(os.path.join(DATA, "VIX_History.csv"))
    vixh["DATE"] = pd.to_datetime(vixh["DATE"])
    vixh = vixh.set_index("DATE").loc[START:END]
    spike = (vixh["HIGH"] - vixh["CLOSE"].shift(1)) / vixh["CLOSE"].shift(1)
    closemove = (vixh["CLOSE"] - vixh["CLOSE"].shift(1)) / vixh["CLOSE"].shift(1)
    held_short = out5["weight"].shift(0) < 0
    extra = (spike - closemove)[held_short].dropna()
    worst = (spike - closemove)[held_short].nlargest(5)
    print("Intraday VIX high overshoot vs close (short-held days), top 5:")
    for d, v in worst.items():
        print(f"  {d.date()}: VIX intraday high exceeded close-to-close move "
              f"by {v*100:.1f} VIX-%pts (relative)")

    # save daily results
    res[5]["out"].loc[START:END].to_csv(os.path.join(HERE, "daily_5bps.csv"))
    res[15]["out"].loc[START:END, ["ret"]].to_csv(os.path.join(HERE, "daily_15bps.csv"))

    print("\n=== VERDICT INPUTS ===")
    print(f"Claimed: annRet 16.3%, Sharpe 1.0 (2008-01..2025-05, 5bps)")
    print(f"Reproduced 5bps Sharpe : {res[5]['sharpe']:.3f}")
    print(f"Reproduced 15bps Sharpe: {res[15]['sharpe']:.3f}")


if __name__ == "__main__":
    main()
