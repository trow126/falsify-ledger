#!/usr/bin/env python
"""
Entry 02 verification — reproduction of Qiita article
"機械学習による株価予測" (pyman123, https://qiita.com/pyman123/items/70406028c7607102ad83)

Reproduces the article's LSTM pipeline exactly (same data source yfinance 6920.T,
same 70/30 split, same MinMaxScaler-on-full-dataset preprocessing, same model
architecture, batch_size=1, epochs=1), computes RMSE_model on the test period in
price scale, and compares against the frozen naive baseline
(RMSE_naive: predict tomorrow's close = today's close, same test period, same scale).

Modifications vs. article code (all mechanical, recorded in result.md):
  M1. auto_adjust=False in yf.download (new yfinance defaults to True; article-era
      default was False, and the article shows both Close and Adj Close columns).
  M2. Flatten yfinance MultiIndex columns (new yfinance returns (Price, Ticker)
      MultiIndex; article-era returned flat columns; df.filter(["Close"]) fails
      otherwise).
  M3. Fixed random seeds (42) for reproducibility (article sets none).
  M4. Removed matplotlib plotting (headless environment; not verdict-relevant).
  M5. Drop rows with NaN Close (new yfinance returns the current, incomplete
      trading day with NaN Close; article-era data had no NaN — Output 2 states
      "データセットは完全に揃っている").
"""
import json
import random
import sys
from datetime import datetime

import numpy as np

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 42
random.seed(SEED)
np.random.seed(SEED)
import tensorflow as tf  # noqa: E402

tf.random.set_seed(SEED)
tf.config.experimental.enable_op_determinism()

import yfinance as yf  # noqa: E402
from sklearn.preprocessing import MinMaxScaler  # noqa: E402
from sklearn.metrics import mean_squared_error  # noqa: E402
from keras.models import Sequential  # noqa: E402
from keras.layers import Dense, LSTM  # noqa: E402

print("=== library versions ===")
print("python:", sys.version)
print("numpy:", np.__version__)
print("tensorflow:", tf.__version__)
print("yfinance:", yf.__version__)
import sklearn, pandas as pd  # noqa: E402

print("scikit-learn:", sklearn.__version__)
print("pandas:", pd.__version__)
print("data fetch datetime (UTC):", datetime.utcnow().isoformat())

# ---- 4-2 data (article: yf.download("6920.T", start='2018-01-01', end=datetime.now(), interval="1d"))
df = yf.download("6920.T", start="2018-01-01", end=datetime.now(), interval="1d",
                 auto_adjust=False)  # M1
if isinstance(df.columns, pd.MultiIndex):  # M2
    df.columns = df.columns.get_level_values(0)
n_nan = int(df["Close"].isna().sum())
if n_nan:
    print(f"M5: dropping {n_nan} row(s) with NaN Close:",
          [str(d.date()) for d in df.index[df["Close"].isna()]])
    df = df.dropna(subset=["Close"])  # M5
print("rows:", len(df), "| first:", df.index[0].date(), "| last:", df.index[-1].date())
df.to_csv("/home/trow126/falsify-ledger/verification/02/data_6920T.csv")

# ---- 4-3 preprocessing (article: MinMaxScaler fit on FULL dataset -> leakage, kept as-is)
data = df.filter(["Close"])
dataset = data.values
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

# ---- 4-4 split (70% train)
training_data_len = int(np.ceil(len(dataset) * 0.7))
print("training_data_len:", training_data_len)
train_data = scaled_data[0:int(training_data_len), :]

# ---- 4-5 training windows (60-step)
x_train, y_train = [], []
for i in range(60, len(train_data)):
    x_train.append(train_data[i - 60:i, 0])
    y_train.append(train_data[i, 0])
x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
print("x_train shape:", x_train.shape)

# ---- 4-6 model (article architecture, batch_size=1, epochs=1)
model = Sequential()
model.add(LSTM(128, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(LSTM(64, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mean_squared_error")
model.fit(x_train, y_train, batch_size=1, epochs=1)

# ---- 4-7 test set and prediction (article code verbatim)
test_data = scaled_data[training_data_len - 60:, :]
x_test = []
for i in range(60, len(test_data)):
    x_test.append(test_data[i - 60:i, 0])
y_test = dataset[training_data_len:, :]
x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

predictions = model.predict(x_test, verbose=0)
predictions = scaler.inverse_transform(predictions)

rmse_model = float(np.sqrt(mean_squared_error(y_test, predictions)))
print("Test Score: %.2f RMSE (RMSE_model, price scale)" % rmse_model)

# ---- Naive baseline: predict close[t] = close[t-1], identical test period, price scale.
# Test targets are dataset[training_data_len:]; previous-day closes are
# dataset[training_data_len-1:-1].
naive_pred = dataset[training_data_len - 1:-1, :]
assert naive_pred.shape == y_test.shape
rmse_naive = float(np.sqrt(mean_squared_error(y_test, naive_pred)))
print("Naive Score: %.2f RMSE (RMSE_naive, price scale)" % rmse_naive)

# ---- Frozen mechanical verdict
if rmse_naive <= rmse_model * 1.05:
    verdict = "KILL"
elif rmse_model < rmse_naive * 0.80:
    verdict = "SURVIVE"
else:
    verdict = "REVISE"
print(f"VERDICT: {verdict}  (RMSE_naive={rmse_naive:.4f}, RMSE_model={rmse_model:.4f}, "
      f"1.05*RMSE_model={1.05*rmse_model:.4f}, 0.80*RMSE_naive={0.80*rmse_naive:.4f})")

# ---- Secondary observations (report only, NOT verdict-driving) ----------------
print("\n=== secondary observations ===")

# (a) MinMaxScaler leakage: scaler fit on full dataset vs. train-only fit.
train_min, train_max = dataset[:training_data_len].min(), dataset[:training_data_len].max()
full_min, full_max = dataset.min(), dataset.max()
print(f"(a) scaler fit on FULL dataset: min={full_min:.1f}, max={full_max:.1f}; "
      f"train-only would be: min={train_min:.1f}, max={train_max:.1f}; "
      f"leakage present: {bool(full_max > train_max or full_min < train_min)}")

# (b) test window overlap: test_data starts at training_data_len-60, so the first
# 60 test inputs come from the training period (standard warm-up; targets do not overlap).
print(f"(b) test_data starts at index {training_data_len-60} "
      f"(training period ends at {training_data_len-1}); first test input window "
      f"uses 60 training-period closes as features; test TARGETS start at "
      f"{training_data_len} (no target overlap).")

# (c) simple signal: buy next day iff prediction > previous close; pre-cost return.
prev_close = dataset[training_data_len - 1:-1, 0]
actual = y_test[:, 0]
signal = (predictions[:, 0] > prev_close).astype(int)
daily_ret = actual / prev_close - 1.0
strat_ret = signal * daily_ret
cum_strat = float(np.prod(1 + strat_ret) - 1)
cum_bh = float(np.prod(1 + daily_ret) - 1)
print(f"(c) signal 'buy if pred > prev close': days long {signal.sum()}/{len(signal)}, "
      f"cumulative pre-cost return {cum_strat*100:.2f}% vs buy&hold {cum_bh*100:.2f}% "
      f"over test period")

# machine-readable summary
summary = dict(
    seed=SEED, rows=len(df), first_date=str(df.index[0].date()),
    last_date=str(df.index[-1].date()), training_data_len=int(training_data_len),
    n_test=int(len(y_test)), rmse_model=rmse_model, rmse_naive=rmse_naive,
    verdict=verdict, kill_threshold_rmse_model_x105=1.05 * rmse_model,
    survive_threshold_rmse_naive_x080=0.80 * rmse_naive,
    signal_days_long=int(signal.sum()), signal_cum_return_precost=cum_strat,
    buyhold_cum_return=cum_bh,
    versions=dict(python=sys.version.split()[0], numpy=np.__version__,
                  tensorflow=tf.__version__, yfinance=yf.__version__,
                  sklearn=sklearn.__version__, pandas=pd.__version__),
)
with open("/home/trow126/falsify-ledger/verification/02/summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("\nsummary written to summary.json")
