# 05 — Object AI Scripts, Subscripts, Indirect Action Dispatch

**Status:** PARTIAL; one producer-backed chain, a mechanical atlas and native partial address lift. Evidence [0503](../analysis/RAW0B_AI_DISPATCH_NATIVE_0503.md), [0504](../analysis/RAW0B_AI_SCRIPT_SEED_0504.md), [action atlas](../analysis/RAW0B_ACTION_DISPATCH_ATLAS.md).

## Four-byte record model

In raw VRC6 bank $0B, $BD11-$BD66 handles object AI scripts after stopwatch/zero-script/$27 conditional checks. The per-object **$05EF,X** script ID chooses a 16-bit pointer from the $BEA3 little-endian table (double the 8-bit ID); **$05C1,X** selects a four-byte record offset (4×index in 8-bit arithmetic). The record's first byte is the action, with remaining three bytes action-specific parameters.

The action is doubled by `ASL A`, and the carry/high bit chooses the word table:
- action $00-$7F → word at $BD67 + 2×action;
- action $80-$FF → word at $BE67 + 2×(action-$80).

The two terminal `JMP ($0000)` sites are at $BD56/$BD64. Mechanical interpretation of 256 byte values yields **217 distinct target words**, but does **not prove 256 live actions**. The $9E mechanical slot overlaps script-pointer data at $BEA3 and points to fallback record $BF79, a concrete warning against blanket code promotion.

## One documented JP producer chain

Raw bank-$0B:$B503 sets script ID **$1B** into $05EF,X, then $B516 resets $05C1,X=0. Pointer $BED9 points to $B03A. The first three exactly justified records are:

| Record | Bytes | Action | Raw-$0B handler |
|---|---|---|---|
| $B03A | 0B 0E 46 00 | $0B | $8519 |
| $B03E | 45 30 00 00 | $45 | $965D |
| $B042 | 46 00 00 00 | $46 | $96B4 |

Action $0B updates animation/object data and advances the record index; $45 uses five bounded 8-entry movement/parameter tables at $968C-$96B3 and advances the index; $46 decrements a timer and uses movement/cleanup logic. Its graph calls fixed $FC1F. **Further record liveness is not inferred** merely by contiguous data.

## Candidate directory ≠ live gameplay

Mechanical reading of 107 script IDs ($00-$6A) gives 72 distinct pointers, 71 candidate aligned starts, and 792 four-byte lattice positions in $A4A6-$B105. Only a *subset* has proved producer/action chains. Candidate IDs $24/$25/$26 contain actions $5D/$5F/$89 leading to handlers $8DC6/$8E10/$8DF9 and possible fixed $FC17 calls, but [0507](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md) explicitly rejects four tempting immediate-byte occurrences as **direct** ID producers. These three IDs remain structurally identified, **not live-proven**.

## Native boundary

[AI address lift](../src/ai_script_dispatch.hpp) and [test](../tests/ai_script_dispatch_test.cpp) cover all 256 mechanical action inputs and flag/address arithmetic under mapped CPU reads. The primitive **does not** run all BD11 stopwatch/$27 checks, mutate complete CPU state, or establish dynamic/temporal liveness. Modding should preserve raw records and unknown fields, and use a separate extension format for extra scripts. See [11](11_PROGRAMMER_MODDER_REFERENCE.md).
