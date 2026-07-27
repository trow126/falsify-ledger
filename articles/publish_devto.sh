#!/usr/bin/env bash
# dev.to へ英語記事を投稿する。ユーザー自身が実行する想定:
#   bash ~/falsify-ledger/articles/publish_devto.sh
# API key は falsify-ledger/.env の DEVTO_API_KEY から読み、画面には出力しない。
set -euo pipefail

ENV_FILE="$HOME/falsify-ledger/.env"
ARTICLE="$HOME/falsify-ledger/articles/en-tradingagents-baseline.md"

set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

if [ -z "${DEVTO_API_KEY:-}" ]; then
  echo "ERROR: DEVTO_API_KEY not found in $ENV_FILE" >&2
  exit 1
fi

python3 - "$ARTICLE" <<'PY'
import json, os, sys, urllib.request

path = sys.argv[1]
lines = open(path).read().split("\n")
# 先頭の H1 をタイトルに、本文はそれ以降（cross-post 注記の行は除く）
title = lines[0].lstrip("# ").strip()
body_lines = [l for l in lines[1:] if not l.startswith("*Cross-post source")]
body = "\n".join(body_lines).strip()

payload = {
    "article": {
        "title": title,
        "published": True,
        "body_markdown": body,
        "tags": ["ai", "machinelearning", "datascience", "python"],
    }
}
req = urllib.request.Request(
    "https://dev.to/api/articles",
    data=json.dumps(payload).encode(),
    headers={
        "api-key": os.environ["DEVTO_API_KEY"],
        "Content-Type": "application/json",
        "User-Agent": "falsify-ledger-publisher",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req) as r:
        d = json.load(r)
        print("PUBLISHED:", d.get("url"))
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:500])
    sys.exit(1)
PY
