# 0506 — Cross-bank room-object loader, temporary PRG read, and AI-script link atlas

ROM source SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. All findings are ROM-specific. These are **mechanical/conditional** graphs unless identified as prior-verified live producers.

## Fixed $FB96-$FBA4: actual mapper transaction

The exact 15-byte fixed helper executes `LDA #$0E; JSR $E2D0; LDA ($08),Y; PHA; LDA #$0A; JSR $E2D0; PLA; RTS`. Fixed `E2D0: STA $23; STA $8000; RTS` selects the VRC6 16-KiB switchable window.

A call under raw-bank-$0A context therefore selects raw PRG bank **$0E** for one mapped indirect-indexed CPU read and restores raw bank **$0A** before returning. **It is not a ROM-array lookup with a persistent $0E bank or an arbitrary clamp.** It also updates $23 and the mapper register; the C++ partial lift implements those bus-visible operations and final A/N/Z, but not the stack pushes/cycle timing.

## Raw bank $0A loader and conditional state dispatch

At $B597 appears `JSR $B689`; $B689 uses `LDA $68; JSR $E7FB`, with **11 encoded pointer pairs**. The first encoded target is $B6A4; its body can call $B7F7, after a precheck. $B7F7-$B872 uses $B8C2 pointer pairs selected by $07A0 and **11 actual JSR $FB96 opcodes**, extracting room and object fields into $34/$35/$36, RAM $54 and $72, $07A1, $054E and slot arrays. Critically, $B825 AND #$0F / $B827 STA $54 establishes **$54=0..15 on this specific loader path**. It does not prove a **global** $54 bound or $FD62,Y bound, since other writers and the separate $14 producer remain open.

The **live $68 selector domain and the inbound mapper context for B597/B689 are not proved** merely by this encoded table. Therefore **none of the fixed $FB96-$FBA4 or raw $0A B7F7-B872 bytes are newly promoted**; they remain reproducible candidate code until their producer/entry context is closed.

## AI scripts and fixed $FC17 linkage

107 mechanical script-ID pointer slots ($00-$6A) contain 72 distinct word values, 71 aligned candidate starts, and 792 provisional four-byte lattice positions in $A4A6-$B105. These are **not** 792 live records.

Three concrete structural links:

| Candidate script ID | Candidate four-byte-record address | Action byte | Mechanical handler |
|---|---|---|---|
| $24 | $A626 | $5D | $8DC6 |
| $25 | $AE1A | $5F | $8E10 |
| $26 | $AE6E | $89 | $8DF9 |

The corresponding candidate handler families have raw calls to fixed $FC17. The eight bytes $FC17-$FC1E are **still unclaimed**: no live producer for script IDs $24/$25/$26 and no executable inbound mapper-specific call context has been proven yet.

The whole-ROM candidate shortlists are unchanged: 156 raw JSR-pattern sites pointing at five fixed-tail entries and 37 raw `LDA #id; STA $05EF,X` script-ID initialization patterns. Most are not yet classified as executable instructions.

## Tested native primitive and reproducible audit

- `src/temporary_prg_bank_read.hpp`: partial bus-aware lift, explicit $23/$8000 writes and 16-bit read.
- `tests/temporary_prg_bank_read_test.cpp`: 65,536 combinations of pointer-low and Y under actual Japanese bank-$0E ROM data, plus a 16-bit wrap case (**65,537 cases**) with bank-restore and write-order assertions.
- `tools/audit_crossbank_ai_atlas_0506.py`: ROM fingerprint, exact $FB96 and $E2D0 opcodes, $B689 dispatch and $B7F7 calls, 107-ID candidate atlas, three selected action-handler correlations, and raw pattern counts.

Tests demonstrate the partial native bus transaction, **not frame-level CPU/PPU/runtime parity**.

This checkpoint adds **zero strictly verified PRG bytes**, because no new live producer/mapper context has been proved for candidate roots. Verified floor remains **49,399 / 262,144 = 18.8442%**; VPP remains **24/100**. The physical fixed investigation frontier is PRG31:$FB96, including the preexisting unclaimed gaps.

### 0507 planned proof targets

1. Trace state selector $68 and active raw-bank-$0A mapping to $B597/$B689 and its index-zero path.
2. Trace actual script ID $24/$25/$26 producers; promote $FC17 only when a proven inbound executable path uses it.
3. Disambiguate other $54/$14 write paths and the shared $10 final-writer problem.
4. Continue native execution/frame-level parity infrastructure separately from structural classification.
