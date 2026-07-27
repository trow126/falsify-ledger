# Entry 02 verification result — Qiita「機械学習による株価予測」LSTM

- entry: `/home/trow126/falsify-ledger/entries/02-qiita-lstm-stock-prediction.md`（凍結済み、未編集）
- 対象記事: https://qiita.com/pyman123/items/70406028c7607102ad83
- 実行日 (UTC): 2026-07-27（データ取得 2026-07-27T19:47:55Z）
- 実行者: Claude Code 検証エージェント

## Verdict（Primary kill condition の機械的適用）

| 量 | 値（価格スケール、円） |
|---|---|
| RMSE_model（記事 LSTM、テスト期間、逆変換後） | **2123.49** |
| RMSE_naive（前日終値コピー、同一テスト期間） | **1231.02** |
| KILL 閾値: RMSE_model × 1.05 | 2229.67 |
| SURVIVE 閾値: RMSE_naive × 0.80 | 984.82 |

判定: `RMSE_naive (1231.02) ≤ RMSE_model × 1.05 (2229.67)` → **KILL**

ナイーブ「前日終値をそのまま予測」の方が LSTM より **42% 低い** RMSE。記事の
「見た目は精度が高い」チャートの実体は 1 日遅れコピー錯視であり、それを下回る。
予測主張は無効。

### Seed robustness（判定の頑健性確認、verdict は seed=42 の主実行）

| seed | RMSE_model | RMSE_naive | 判定 |
|---|---|---|---|
| 42（主実行） | 2123.49 | 1231.02 | KILL |
| 0 | 2830.19 | 1231.02 | KILL |
| 7 | 3373.19 | 1231.02 | KILL |

全 seed で KILL。記事は seed 未設定・epochs=1 のため実行毎に揺れるが、いずれも
ナイーブに大差で負ける。

## 再現条件

- データ: yfinance `6920.T`, start=2018-01-01, end=now, interval=1d, auto_adjust=False。
  2103 営業日（2018-01-01〜2026-07-24）。snapshot: `data_6920T.csv`
- 分割: 記事どおり `training_data_len = ceil(len*0.7) = 1473`、テスト 630 日
- 前処理: 記事どおり MinMaxScaler(0,1) を**全期間で fit**（leakage も記事のまま再現）
- モデル: 記事どおり LSTM(128, return_sequences)→LSTM(64)→Dense(25)→Dense(1)、
  adam / MSE、batch_size=1、epochs=1
- RMSE: 両者とも逆変換後の価格スケールで `sqrt(mean_squared_error)`。
  y_test = dataset[1473:]（生値）、naive_pred = dataset[1472:-1]（前日終値）
- 乱数 seed: 42（python/numpy/tensorflow、`enable_op_determinism()` 有効）

### ライブラリ版数

Python 3.12.13 / numpy 2.5.1 / tensorflow-cpu 2.21.0 / yfinance 1.5.2 /
scikit-learn 1.9.0 / pandas 3.0.5（uv 管理の venv、全て無料、支出 ¥0）

## 記事コードへの機械的修正（全記録、合計 30 分未満）

1. **M1**: `yf.download(..., auto_adjust=False)` を明示。新 yfinance は
   auto_adjust=True が既定で、記事当時の既定（False、Adj Close 列あり）に合わせた。
2. **M2**: 新 yfinance の MultiIndex 列 `(Price, Ticker)` をフラット化
   （`df.filter(["Close"])` が記事当時の挙動になるように）。
3. **M3**: 乱数 seed 固定（記事は未設定）。再現性のためで、判定は seed に依らず KILL。
4. **M4**: matplotlib 描画を削除（headless 環境、verdict 非関与）。
5. **M5**: Close が NaN の行を除去。新 yfinance が当日（2026-07-27）の未確定バーを
   NaN Close で返すため（1 行のみ）。記事当時のデータは「完全に揃っている」と記事内で確認済み。

モデル・分割・前処理・評価のロジックには一切手を入れていない。

## Secondary observations（報告のみ、verdict 非使用）

- **(a) MinMaxScaler leakage: あり。** scaler は全期間（min=1272.5, max=57490）で
  fit されているが、訓練期間のみなら max=35600。テスト期間の高値情報が訓練時の
  スケーリングに漏れている。ただし本件の KILL はこの leakage を記事のまま残した上で
  成立しており、leakage 修正はモデルをさらに不利にする方向。
- **(b) テスト切り出しの重なり:** `test_data = scaled_data[training_data_len-60:]` の
  ため、最初の 60 本の入力窓は訓練期間の終値を特徴量として使う（標準的な warm-up）。
  テスト**ターゲット**は index 1473 以降で訓練ターゲットと重複なし。ターゲット重複型の
  leakage は無し。
- **(c) 単純シグナル変換:** 「予測 > 前日終値なら翌日買い」で、テスト期間 630 日中
  544 日ロング、コスト前累積リターン **+14.08%**。同期間 buy&hold は **+21.98%**。
  コスト前ですら buy&hold に劣後し、取引コスト（544 往復）を引けばさらに悪化する。
  経済的価値も確認できない。

## 作成ファイル

| ファイル | 内容 |
|---|---|
| `article_raw.md` | 記事本文の snapshot（Qiita .md エンドポイント） |
| `reproduce.py` | 再現＋ナイーブ比較＋判定＋secondary（単一スクリプト。naive baseline も本スクリプト内） |
| `data_6920T.csv` | 使用データの snapshot（NaN 除去後） |
| `run_log.txt` | 主実行（seed=42）の実行ログ（progress bar 除去済み） |
| `seed_robustness.txt` | seed 0/7 の追試ログ |
| `summary.json` / `summary_seed42.json` | 機械可読サマリ（seed=42） |
| `result.md` | 本ファイル |

## 結論

事前登録（P(kill)=0.95）どおり **KILL**。「LSTM で株価を高精度予測」の実体は
price-level 回帰による 1 日遅れコピーで、しかもそのコピーにすら RMSE で 42% 劣る。
entries/02 の verdict 欄更新は台帳編集禁止のため行っていない（owner 判断待ち）。
