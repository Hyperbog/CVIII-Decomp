#!/usr/bin/env bash
# 1100-frame authenticated original Japanese ROM state-transition test.
# Private original media, savestates and Mesen DLL never committed.
set -euo pipefail
[[ "$#" == 3 ]] || { echo 'usage: run_mesen_state13_0549.sh JP_ROM MESEN_AGENT_DIR PRIVATE_OUT' >&2; exit 2; }
ROM="$1";BIN="$2";OUT="$3"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$OUT"
python3 - "$ROM" "$BIN" "$ROOT" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[3])/'JP/decomp/tools'))
from audit_mesen_state13_0549 import authenticate
authenticate(Path(sys.argv[1]),Path(sys.argv[2]))
print('Authenticated original JP ROM, Mesen agent and core')
PY
M="$BIN/mesen-agent"; LUA="$ROOT/JP/decomp/tools/mesen_0549_state13_provenance.lua"
"$M" "$ROM" --home "$OUT/home-play" --frames 520 --timeout 120 \
    --lua "$LUA" --input '0:start@90-92' --input '0:start@180-182' \
    --input '0:start@300-302' --input '0:right@370-520' \
    --input '0:a@460-469' --input '0:b@470-475' \
    --save-state "$OUT/play520.mss" > "$OUT/play520.jsonl"
"$M" "$ROM" --home "$OUT/home-prayer" --load-state "$OUT/play520.mss" \
    --frames 220 --timeout 120 --lua "$LUA" \
    --input '0:start@10-11' --input '0:right@125-210' --input '0:b@130-132' \
    --save-state "$OUT/stage220.mss" > "$OUT/stage220.jsonl"
"$M" "$ROM" --home "$OUT/home-stage" --load-state "$OUT/stage220.mss" \
    --frames 360 --timeout 120 --lua "$LUA" \
    --input '0:start@5-6' --input '0:right@90-325' --input '0:b@130-132' \
    --input '0:a@270-272' --save-state "$OUT/stage360.mss" > "$OUT/stage360.jsonl"
python3 "$ROOT/JP/decomp/tools/audit_mesen_state13_0549.py" --rom "$ROM" --emulator "$BIN" \
    --segment play520 "$OUT/play520.jsonl" --segment stage220 "$OUT/stage220.jsonl" \
    --segment stage360 "$OUT/stage360.jsonl" --out "$OUT/state13_evidence.json"
echo 'Only derived bounded report may be shared; keep savestates, ROM and full emulator logs private.'
