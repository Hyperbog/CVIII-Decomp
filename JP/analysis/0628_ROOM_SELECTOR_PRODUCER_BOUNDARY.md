# JP0628 — Raw0A room selector producer/consumer bounds (R-002)

**Evidence: original Japanese ROM, instruction-stepped but CONDITIONAL.**
This is not a gameplay/liveness trace. No new strict PRG bytes certified.

## Source code executed

The [JP0628 bounded audit](../tools/audit_room_selector_window_0628.py)
authenticates original retail Japanese mapper-24 ROM SHA-256
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
and physical raw0A 16KiB SHA-256
1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8.

It interprets original, checked 6502 bytes under explicitly assumed
separate 16KiB bank mappings:

1. **Raw01 CPU $BB57–$BB61**:
   LDA $30; LSR A; TAY; LDA $BB62,Y; STA $07A0; RTS.
   Runs all 256 possible input RAM[$30] values.
2. **Raw0A CPU $B7F7–$B805**:
   LDA $07A0; ASL A; TAY; LDA $B8C2,Y; STA $08;
   LDA $B8C3,Y; STA $09.
   Runs all 256 possible selector RAM[$07A0] values,
   checking each resulting little-endian pointer against a separate
   direct physical-bank byte decoder.

The audit stops before the next stream dereference, mapper-bank change
or object record parser. It does **not** execute a demonstrated live
bank01-to-bank0A call chain or simulate NMI/IRQ interleaving.

## Complete conditional selector results

The five documented original raw0A pointer roots, at $B8C2–$B8CB,
are $BEA4, $BEDB, $BF03, $BE8B, and $BF1C.

| Raw0A selector result | Count |
|---|---:|
| Pointer equals one of five documented stream roots | 10 |
| Pointer inside $8000–$BFFF but not one of those roots | 26 |
| Pointer outside $8000–$BFFF | 220 |
| **Total** | **256** |

The ten stream-root matches comprise selectors 0–4 and 128–132:
the original 8-bit ASL wraps the table index every 128 input values.
High-bit aliases are **not** thereby proven safe or live.

**Conditional counterexample:** With RAM[$30]=$06 at raw01:$BB57,
the original raw01:$BB65 table byte assigns RAM[$07A0]=$35.
If that value is subsequently presented to raw0A:$B7F7, its computed
pointer becomes $FF63, **outside the expected switchable bank0E
$8000–$BFFF window**. The CPU address $FF63 is still in the fixed
bank's address window. This is NOT proof of a crash, illegal CPU
memory access, game exploit, or actual producer-to-consumer liveness.

This explicitly refutes using the five-table-item count as a
*global selector-domain proof*. The classification of 26 other
within-window pointers does not validate their record structures.

The reproducible non-lossless [report JSON](0628_room_selector_window_report.json)
stores exact aggregate findings, with 0 new certified bytes.

## Reproduce

~~~sh
python3 JP/tools/audit_room_selector_window_0628.py --smoke
python3 JP/tools/audit_room_selector_window_0628.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --out /tmp/jp0628_report.json
~~~

**Actually executed, PASS:** all 256 producer values and 256
consumer values on the original authenticated ROM; pointer comparison,
high-bit wrap behavior, source instruction signatures, raw0A bank SHA,
the $35->$FF63 conditional mismatch. Synthetic smoke also PASS
including refusal of a deliberately altered original opcode. The
locally tested source matches committed Git blob
8ce922e80b3a0f742383175c572f05f0838e955f.

**Additionally replayed against the original ROM:** all three fixed
PRG31 SHA-256 fingerprints from the recovery ledger ($FB76–$FB95,
$FB96–$FBB5, and $FB96–$FFFF); all matched. CI runs only the ROM-free
JP0628 smoke. The retail-ROM mode is local and must remain private.

## Exact unresolved obligation

**R-002 remains OPEN.** The next requirement is an independent
Mesen gameplay trace with physical bank state, source PC and
write-to-read order for the original RAM[$07A0] producers and raw0A
$B7F7 consumer, including intervening NMI/IRQ and control flow.
Only then can we prove which indices are truly live, whether
the raw01 producer is even a relevant predecessor, and which
room-data types should become certified. No alternate guard or
new original-game fault is inferred.

Existing 0538 raw0A census unchanged: 2,162 previously authenticated
instruction bytes, 168 audited data bytes, 2,910 candidate-code
bytes, 7,460 structural-only data bytes and 3,684 unresolved.

**Certification unchanged:** strict PRG 49,504 / 262,144
(18.8843%), VPP 27/100, checkpoint 0508, fixed frontier $FB96.
No edits to JP/analysis/RESUME_STATE.json.
