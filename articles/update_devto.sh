#!/usr/bin/env bash
# dev.to の既存記事を articles/en-tradingagents-baseline.md の内容で更新する。
# ユーザー自身が実行する想定: bash ~/falsify-ledger/articles/update_devto.sh
set -euo pipefail

ENV_FILE="$HOME/falsify-ledger/.env"
ARTICLE="$HOME/falsify-ledger/articles/en-tradingagents-baseline.md"

set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

[ -n "${DEVTO_API_KEY:-}" ] || { echo "ERROR: DEVTO_API_KEY not set" >&2; exit 1; }

python3 - "$ARTICLE" <<'PY'
import json, os, sys, urllib.request

key = os.environ["DEVTO_API_KEY"]
headers = {"api-key": key, "Content-Type": "application/json",
           "User-Agent": "falsify-ledger-publisher"}

# 自分の記事一覧から対象記事の数値 ID を特定する
req = urllib.request.Request("https://dev.to/api/articles/me?per_page=30", headers=headers)
mine = json.load(urllib.request.urlopen(req))
target = next((a for a in mine if "most-starred-llm-trading-paper" in a["slug"]), None)
if not target:
    print("ERROR: article not found in /articles/me")
    sys.exit(1)

lines = open(sys.argv[1]).read().split("\n")
title = lines[0].lstrip("# ").strip()
body = "\n".join(l for l in lines[1:] if not l.startswith("*Cross-post source")).strip()

payload = {"article": {"title": title, "body_markdown": body, "published": True}}
req = urllib.request.Request(f"https://dev.to/api/articles/{target['id']}",
                             data=json.dumps(payload).encode(), headers=headers,
                             method="PUT")
with urllib.request.urlopen(req) as r:
    d = json.load(r)
    print("UPDATED:", d.get("url"))
PY
