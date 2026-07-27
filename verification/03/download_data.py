#!/usr/bin/env python3
"""Download free data for Concretum VIX strategy reproduction (entry 03).

Sources (all free, no cash cost):
- CBOE: VIX_History.csv, VIX3M_History.csv (official index closes)
- CBOE: VIX futures daily settles (archive CSVs pre-2014 + per-expiry CSVs after)
- SPY adjusted closes: yfinance (fallback: stooq)
"""
import datetime as dt
import io
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)
os.makedirs(os.path.join(DATA, "vx"), exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-reproduction"}


def fetch(url, dest, retries=2):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
            if len(body) < 50:
                return False
            with open(dest, "wb") as f:
                f.write(body)
            return True
        except Exception as e:
            if i == retries:
                return False
            time.sleep(1 + i)
    return False


def third_friday(year, month):
    d = dt.date(year, month, 15)
    while d.weekday() != 4:  # Friday
        d += dt.timedelta(days=1)
    return d


def vx_settlement(year, month):
    """VIX futures final settlement: Wednesday 30 days before 3rd Friday of the
    following month (holiday shifts handled by probing nearby dates on 404)."""
    ny, nm = (year + 1, 1) if month == 12 else (year, month + 1)
    return third_friday(ny, nm) - dt.timedelta(days=30)


MONTH_CODE = {1: "F", 2: "G", 3: "H", 4: "J", 5: "K", 6: "M",
              7: "N", 8: "Q", 9: "U", 10: "V", 11: "X", 12: "Z"}


def main():
    ok = fetch("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
               os.path.join(DATA, "VIX_History.csv"))
    print("VIX_History:", ok)
    ok = fetch("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv",
               os.path.join(DATA, "VIX3M_History.csv"))
    print("VIX3M_History:", ok)

    # SPY
    spy_path = os.path.join(DATA, "SPY.csv")
    if not os.path.exists(spy_path):
        got = False
        try:
            sys.path.insert(0, os.path.join(HERE, "venv/lib"))
            import yfinance as yf
            df = yf.download("SPY", start="2007-01-01", end="2025-06-01",
                             auto_adjust=True, progress=False)
            if len(df) > 4000:
                df.to_csv(spy_path)
                got = True
                print("SPY via yfinance:", len(df), "rows")
        except Exception as e:
            print("yfinance failed:", e)
        if not got:
            ok = fetch("https://stooq.com/q/d/l/?s=spy.us&i=d", spy_path)
            print("SPY via stooq:", ok)

    # VIX futures: contracts settling 2007-11 .. 2025-07
    months = []
    y, m = 2007, 11
    while (y, m) <= (2025, 7):
        months.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    n_ok = n_fail = 0
    for (y, m) in months:
        sett = vx_settlement(y, m)
        dest = os.path.join(DATA, "vx", f"VX_{y}-{m:02d}.csv")
        if os.path.exists(dest):
            n_ok += 1
            continue
        got = False
        # new-format per-expiry file (works for contracts ~2013-06 onward)
        for shift in (0, -1, 1, -2, 2, -7, 7):
            d = sett + dt.timedelta(days=shift)
            url = f"https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_{d.isoformat()}.csv"
            if fetch(url, dest, retries=0):
                got = True
                break
        if not got:
            # archive format
            url = f"https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_{MONTH_CODE[m]}{y % 100:02d}_VX.csv"
            got = fetch(url, dest, retries=1)
        if got:
            n_ok += 1
        else:
            n_fail += 1
            print("MISSING contract:", y, m)
    print(f"VX contracts: ok={n_ok} fail={n_fail}")


if __name__ == "__main__":
    main()
