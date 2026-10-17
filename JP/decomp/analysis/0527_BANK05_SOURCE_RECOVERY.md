# 0527 — Recovered raw bank05 script source certificate, historical PRG union 22,085 bytes

Authoritative original Akumajō Densetsu (Japan) retail NES SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (Mapper 24 VRC6). Physical offsets exclude the 16-byte iNES header.

## Exact source/provenance recovered from historical Git

The original checkpoint evidence in `JP/decomp/analysis/RESUME_STATE.json` and the corresponding complete original raw-bank05 parser audits from historic commits `711c0ee21c27` (04FB), `4f35c4789e4c` (04FC), and `5cfbacc99d01` (04FD) pin three **contiguous original source PRG spans**:

| Historical checkpoint | Raw bank05 CPU start | CPU end inclusive | Physical PRG offset | Previous strict bytes | SHA-256 |
|---|---|---|---|---:|---|
| 04FB | $87AE | $9A6A | $0147AE | 4,797 | `58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b` |
| 04FC | $9A6B | $AD96 | $015A6B | 4,908 | `3d34329fd18b7c713f1fe35206868f1b6c0bdfb6127f664410a60fd54a8c46f0` |
| 04FD | $AD97 | $BF05 | $016D97 | 4,463 | `30f4e1640f97c342886a4d5f1a652cbfda41102abbd4760501bcd2915b474a72` |
| **Total** | | | | **14,168** | Verified original retail ROM |

These are **previously certified stream/script command and operand bytes** with original parser/producer proof (84 script metadata references, 72 distinct root addresses across raw bank05); they are **not 14,168 CPU opcode bytes or a new native code translation**. The historical audits distinguished control commands and their variable operands and proved the original parameter bounds for each admitted window. 0527 recovers and independently fingerprints their physical locations, but does not redo original runtime instruction traces.

## Updated physical coverage accounting

The **04FB–0508 known union** is now **79 disjoint exact PRG intervals / 22,085 mapped previously certified bytes** (previous 04FE–0508 union: 76 / 7,917). Remaining older reported strict bytes without a fully restored physical occupancy map: **27,419**. The original 0510–0517 native source inventory is 1,365 physical bytes: 626 already within these historical regions, 739 outside the currently mapped union. None of the 739 may be promoted until the remaining pre-04FB baseline is reconstructed and original source liveness/control-data provenance is met.

Command, from a repository checkout: `python3 JP/decomp/tools/audit_bank05_certificate_0527.py --rom "$ORIGINAL_JP_ROM"`. CI runs a ROM-free exact physical-address/overlap reconciliation; the retail ROM parameter separately authenticates all source SHA-256 hashes. Use `--only-bank05` to audit the three bank05 spans without older manifest dependencies.

## Distinct recomp progress

Symbolic original-6502 mnemonic source from 0525–0526 remains **403/403 byte-exact source bytes** (315 added at 0526). The 14,168 source bytes recovered here are categorized as original verified **game data and script operands**, not additional 6502 assembly. This is source preservation and decompilation provenance work to unblock new strict bytes, not playable native recompilation.

**No inflated certification:** strict PRG stays **49,504 / 262,144**, VPP **27/100**, certified semantic checkpoint **0508**, fixed-bank certified investigation frontier **$FB96**. The next source-mapping target is the pre-04FB historical bank04 and earlier raw-bank certificate evidence.