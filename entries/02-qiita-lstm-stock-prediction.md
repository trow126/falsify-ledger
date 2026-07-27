# Entry 02 — Qiita「機械学習による株価予測」: LSTM 高精度予測の主張

- status: `VERIFIED`
- registered_at: `2026-07-27T19:41:56Z（git commit timestamp を正とする）`
- verdict: **KILL** — ナイーブ「前日終値コピー」の RMSE 1231 円に対し、再現した LSTM の
  RMSE は 2123 円（ナイーブが 42% 低い。seed 0/7 でも全て KILL）。「高精度予測」の実体は
  1 日遅れコピー錯視であり、しかもそのコピーに大差で劣る。詳細は
  `verification/02/result.md`。
- predicted P(kill): **0.95**
- time cap: 2.0 時間
- cash cost cap: ¥0（無料公開データのみ）

## 対象主張（凍結引用）

Qiita 記事「機械学習による株価予測」（172 LGTM、コード全掲載）:

> レーザーテック (6920.T) の株価を LSTM で予測し、予測曲線が実株価とほぼ一致する
> チャートと低い RMSE を提示。「高精度で予測できた」という趣旨の結論。

- 記事: https://qiita.com/pyman123/items/70406028c7607102ad83
- archive snapshot: 登録日に Wayback Machine へ保存済み
  （https://web.archive.org/web/2026*/https://qiita.com/pyman123/items/70406028c7607102ad83）
- データ: yfinance `6920.T`（無料）

これは記事著者個人への批判ではなく、日本語圏で最も複製されている「LSTM 株価予測」
という型（price-level 予測の 1 日遅れコピー錯視）の方法論検証である。同型の指摘は
Qiita 内にも既にある（https://qiita.com/aokikenichi/items/76af61642db30139ce5a）。

## Primary kill condition（唯一の verdict 駆動テスト）

記事のコードを同一データ・同一分割で再現し、テスト期間について次を比較する。

- `RMSE_model`: 記事の LSTM モデルのテスト RMSE（再現実行値）
- `RMSE_naive`: 「前日終値をそのまま予測値とする」ナイーブ予測の同期間 RMSE

判定:

- **KILL**: `RMSE_naive ≤ RMSE_model × 1.05`（ナイーブ予測が同等以下 →「高精度予測」
  の実体は 1 日遅れコピーであり、予測主張は無効）
- **SURVIVE**: `RMSE_model < RMSE_naive × 0.80`（ナイーブを 20% 以上明確に上回る）
- 中間: `REVISE`（数値を報告し、予測能力は限定的と判定）
- コードが現行ライブラリで再現実行できない場合: 修正が 30 分以内で機械的に可能なら
  修正して続行（修正内容を全掲載）。不可能なら `UNVERIFIABLE`。

## Secondary observations（報告のみ、verdict に使わない）

1. MinMaxScaler を全期間で fit していることによる leakage の有無と影響。
2. テストデータ切り出し位置（訓練期間との重なり）の leakage。
3. 予測を単純な売買シグナル（予測が上なら買い）へ変換した場合の取引コスト前リターン。

## Verification procedure

1. 記事コードを notebook 化して再現（45 分）→ `verification/02/`
2. ナイーブ baseline の RMSE 計算（15 分）
3. secondary checks（30 分）
4. 結果と calibration 更新の執筆（30 分）

## Kill hypothesis（P(kill) = 0.95 の理由）

price-level を目的変数にした LSTM は「直近値のコピー」で loss を最小化するのが定番の
失敗型で、チャートの見かけ上の一致と低 RMSE はほぼ常にこれで説明される。結果を
計算する前に登録する。
