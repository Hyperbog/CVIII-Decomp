# Raw-bank $0B action-dispatch atlas

This is an acceleration artifact extracted from the authoritative JP ROM. It resolves the mechanics of the two indirect jumps at `$BD56/$BD64` without pretending that every possible action byte is live in gameplay.

## Dispatcher

The admitted raw-bank `$0B` code loads one action byte from the current four-byte script/state record:

```asm
BD46  LDA ($02),Y
BD48  ASL
BD49  BCS $BD59

; original action $00-$7F
BD4B  TAY
BD4C  LDA $BD67,Y
...
BD56  JMP ($0000)

; original action $80-$FF
BD59  TAY
BD5A  LDA $BE67,Y
...
BD64  JMP ($0000)
```

Because `ASL` leaves `Y = 2*(action & $7F)`, the mechanical address rule is:

```text
action $00-$7F -> word at $BD67 + 2*action
action $80-$FF -> word at $BE67 + 2*(action-$80)
```

`tools/extract_raw0b_action_dispatch.py` materializes all 256 mappings directly from the JP ROM.

## Whole mechanical map

The 512 bytes `$BD67-$BF66` have SHA-256:

```text
eb075c21401906325dc497d6537978590dccf193abc3897d42a4935533800a13
```

Mechanical interpretation:

```text
action slots           256
distinct target words  217
all target words        inside raw-bank CPU $8000-$BFFF
```

This is **not** a claim that all 256 action IDs occur in live scripts.

## Important alias boundary

The secondary interpretation reaches:

```text
$9D -> entry $BEA1
$9E -> entry $BEA3 -> target $BF79
```

`$BEA3` is also used independently by the script-pointer machinery. Thus the ROM permits the same bytes to have different interpretations under different indexing paths.

That makes the producer-domain rule important: do not infer that `$9E-$FF` are live merely because the indirect dispatcher can mechanically index them.

The `$9E` mechanical target `$BF79` begins the fallback script record (`19 00 00 00`), not an independently proven executable action handler. This is direct evidence that table shape alone is insufficient to establish action liveness.

## How this accelerates later work

The former opaque exits `$BD56 JMP ($0000)` and `$BD64 JMP ($0000)` can now be represented as an action-indexed candidate edge set. Future script/state analysis can intersect its proven action IDs with this atlas instead of rediscovering pointer arithmetic.

The generated JSON includes for every action byte the primary/secondary interpretation, exact table-entry CPU address, exact target CPU address, and raw-bank-window validity.

## Coverage accounting

This artifact does **not** add `$BD67-$BF66` to the strict semantically verified byte floor yet. The live action-producer domain remains open.

It is structural candidate coverage, analogous to the whole-PRG and JP↔US atlases.

Reproducible tools:

```text
tools/extract_raw0b_action_dispatch.py
tools/audit_raw0b_action_dispatch.py
```
