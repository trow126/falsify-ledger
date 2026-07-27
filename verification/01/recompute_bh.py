"""Entry 01 primary kill condition: recompute AAPL buy-and-hold total return
over the frozen window 2024-06-19 .. 2024-11-19 (arXiv:2412.20138 states B&H = -5.23%).

Source per frozen procedure: Yahoo Finance daily adjusted close.
Run: python3 recompute_bh.py
"""
import json
import urllib.request
import datetime


def epoch(d):
    return int(datetime.datetime.strptime(d, "%Y-%m-%d")
               .replace(tzinfo=datetime.timezone.utc).timestamp())


URL = (f"https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
       f"?period1={epoch('2024-06-18')}&period2={epoch('2024-11-21')}"
       f"&interval=1d&events=div%2Csplit")

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
data = json.load(urllib.request.urlopen(req))["chart"]["result"][0]
ts = data["timestamp"]
adj = data["indicators"]["adjclose"][0]["adjclose"]
raw = data["indicators"]["quote"][0]["close"]

for label, series in (("adjusted", adj), ("raw", raw)):
    rows = [(datetime.datetime.fromtimestamp(t, datetime.timezone.utc).date().isoformat(), v)
            for t, v in zip(ts, series) if v is not None]
    start = next(r for r in rows if r[0] >= "2024-06-19")
    end = [r for r in rows if r[0] <= "2024-11-19"][-1]
    bh = end[1] / start[1] - 1
    print(f"{label}: {start[0]} {start[1]:.2f} -> {end[0]} {end[1]:.2f}  B&H = {bh * 100:.2f}%")
