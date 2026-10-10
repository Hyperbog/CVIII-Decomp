#!/usr/bin/env bash
# Reproduce independent Mesen2 original-JP Stage1 branch CDLs locally.
# Inputs: private exact JP ROM, SHA-pinned extracted mesen-agent folder, private output dir.
# NEVER commit ROM, local CDL, screenshots or Mesen savestates.
set -euo pipefail
[[ $# == 3 ]] || { echo "Usage: $0 JP_ROM MESEN_BIN_DIR PRIVATE_OUTPUT_DIR" >&2; exit 2; }
ROM="$1";EMUL="$2";OUT="$3"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$OUT"
python3 - "$ROM" "$EMUL" <<'PY'
import sys,hashlib
from pathlib import Path
got=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert got(sys.argv[1])=="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
assert got(Path(sys.argv[2])/"mesen-agent")=="95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0"
assert got(Path(sys.argv[2])/"MesenCore.so")=="fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1"
print("original JP ROM and independent Mesen build SHA: OK")
PY
M="$EMUL/mesen-agent"
LUA="$ROOT/JP/tools/mesen_0508_frame_state.lua"
run() {
  local tag="$1" frames="$2" prior="$3";shift 3
  local state=()
  if [[ "$prior" != - ]];then
    local old="$prior"
    [[ "$prior" == play520 || "$prior" == stage220 || "$prior" == stage360 ]] || old="${prior}_1200"
    state=(--load-state "$OUT/${old}.mss")
  fi
  local shot=()
  [[ "$tag" == stage360 || "$tag" == right_jump_1200 || "$tag" == keepjump_1200 ]] && shot=(--screenshot "$OUT/${tag}.png")
  "$M" "$ROM" --home "$OUT/home-${tag}" "${state[@]}" \
    --frames "$frames" --timeout 120 --lua "$LUA" \
    --save-cdl "NesPrgRom=$OUT/${tag}.cdl" --save-state "$OUT/${tag}.mss" \
    "${shot[@]}" "$@" > "$OUT/${tag}.jsonl"
  echo "Mesen reference: $tag $frames frames"
}
run play520 520 - --input '0:start@90-92' --input '0:start@180-182' \
  --input '0:start@300-302' --input '0:right@370-520' \
  --input '0:a@460-469' --input '0:b@470-475'
run stage220 220 play520 --input '0:start@10-11' --input '0:right@125-210' --input '0:b@130-132'
run stage360 360 stage220 --input '0:start@5-6' --input '0:right@90-325' \
  --input '0:b@130-132' --input '0:a@270-272'
run right_1200 1200 stage360 --input '0:right@1-1200'
run idle_1200 1200 stage360
jump=()
for n in $(seq 45 100 945);do jump+=(--input "0:a@$n-$((n+10))");done
run right_jump_1200 1200 stage360 --input '0:right@1-1200' "${jump[@]}"
whip=()
for n in $(seq 25 80 905);do whip+=(--input "0:b@$n-$((n+9))");done
run right_whip_1200 1200 stage360 --input '0:right@1-1200' "${whip[@]}"
jump=()
for n in $(seq 50 110 1150);do jump+=(--input "0:a@$n-$((n+12))");done
run keepjump_1200 1200 right_jump --input '0:right@1-1200' "${jump[@]}"
buttons=()
for n in $(seq 20 75 1120);do buttons+=(--input "0:b@$n-$((n+10))");done
for n in $(seq 80 160 1120);do buttons+=(--input "0:a@$n-$((n+15))");done
run keepwhip_1200 1200 right_jump --input '0:right@1-1200' "${buttons[@]}"
run holdjump_1200 1200 right_jump --input '0:right@1-1200' \
  --input '0:a@1-1200' --input '0:b@200-215' --input '0:b@400-415'
python3 "$ROOT/JP/tools/audit_mesen_stage1_branch_0508.py" "$ROM" "$EMUL" "$OUT" "$OUT/branch_hash_only_report.json"
echo "Original executable/ROM/CDL/savestate/screenshots remain private to $OUT"
