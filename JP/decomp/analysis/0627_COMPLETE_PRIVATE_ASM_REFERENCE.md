# JP0627 — Complete private assembly reference and fixed-vector anchors

## Actual result

The user-provided original Japanese Akumajou Densetsu ROM authenticates as
SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28.
It contains a 16-byte iNES header, 262,144 PRG bytes (32 physical 8 KiB
banks), 131,072 CHR bytes (16 physical 8 KiB banks), totaling **393,232**.

[JP0627 generator](../tools/build_private_asm_reference_0627.py)
recreates a **complete private physical-bank source reference**:
- 32 PRG/prg_00.asm ... PRG/prg_31.asm byte listings
- 16 CHR/chr_00.asm ... CHR/chr_15.asm graphics byte listings
- root ROM.asm and header.asm, manifest.json with per-bank SHA-256
- physical_offsets.tsv, keyed by region, bank, bank offset, physical
  offset, file offset and address-context qualification

It re-parses the generated .byte and .word statements and asserts
the exact full 393,232-byte original ROM image and SHA-256 match.
PRG31 is fixed at CPU $E000-$FFFF; other PRG mappings are marked
**mapper-dependent** rather than inventing specific CPU placements.

**The generated assembly listings contain copyrighted original ROM
bytes and must stay outside Git.** The generator refuses output under
a Git checkout. Only the generator, deterministic ROM-free tests and
non-lossless analysis findings belong in this repository.

## How to reproduce, from repository root

~~~sh
python3 JP/decomp/tools/test_private_asm_reference_0627.py
python3 JP/decomp/tools/test_private_asm_reference_0627.py --rom "/private/Akumajou Densetsu (Japan).nes"
python3 JP/decomp/tools/build_private_asm_reference_0627.py --rom "/private/Akumajou Densetsu (Japan).nes" --out "/private/JP-asm-reference"
~~~

The tests include synthetic 48-bank output regeneration, deterministic
hashes, byte-replay comparison, vector addresses, changed-input refusal,
malformed include refusal and protection against ROM-equivalent output
into a Git checkout. Windows and Linux CI run synthetic-only tests;
the commercial ROM never enters public CI.

## Newly consolidated original-ROM structural evidence: PRG31 vectors

The last six bytes of the fixed 8 KiB PRG31 bank are hardware vectors,
**not executable instructions**.

| Vector | CPU vector | PRG31 pointer | Original ROM file | Destination CPU | Destination PRG31 offset |
|---|---|---|---|---|---|
| NMI | $FFFA | +$1FFA | $4000A | $E057 | +$0057 |
| Reset | $FFFC | +$1FFC | $4000C | $E00B | +$000B |
| IRQ/BRK | $FFFE | +$1FFE | $4000E | $E0F5 | +$00F5 |

The original bytes at these three vector destinations permit the
following concrete entrypoint-prefix decoding; this is **not a new
runtime parity proof or new certified-byte award**.

~~~asm
; RESET: PRG31+$000B, file+$3E01B
E00B  D8          CLD
E00C  78          SEI
E00D  AD 02 20    LDA $2002
E010  10 FB       BPL $E00D

; NMI: PRG31+$0057, file+$3E067
E057  48          PHA
E058  8A          TXA
E059  48          PHA
E05A  98          TYA
E05B  48          PHA
E05C  AD 02 20    LDA $2002

; IRQ/BRK: PRG31+$00F5, file+$3E105
E0F5  48          PHA
E0F6  8A          TXA
E0F7  48          PHA
E0F8  98          TYA
E0F9  48          PHA
E0FA  A5 00       LDA $00
E0FC  48          PHA
~~~

These entrypoint locations should seed bank-aware CFG analysis, but
identifying initial instructions is **not** equivalent to completing
routine semantics, VRC6 mapper context, IRQ scheduling or game parity.

## Relationship to existing tools and future annotation

- [Whole-PRG Atlas](../docs/WHOLE_PRG_ATLAS.md) provides aggressive
  candidate opcode/xref discovery. Every-offset decoding is speculative.
- [0529 whole-cartridge source generator](0529_WHOLE_CART_BANK_RECOMP.md)
  already emits symbolic 6502 code for certified spans and .byte for
  unknown bytes; it remains authoritative for proven source lifting.
- JP0627 is the **lossless physical byte-address navigation baseline**.
  Do not duplicate or replace verified mnemonic lifts with guessed code.
  Use the new per-bank offsets to cross-reference 0529/0538 mnemonic
  sources, live traces, and future code/data annotations.

**Actually run on original ROM:** 393,232/393,232 exact assembly byte
reconstruction; all 48 banks and all three fixed vectors. **Actually
run ROM-free:** deterministic regeneration and failure-injection tests.
Generated source/test were checked against committed Git blob hashes.
CI wiring committed; GitHub Actions outcomes not independently observed.

**Strict decompilation certification unchanged:** 49,504/262,144 PRG
bytes (18.8843%), VPP 27/100, checkpoint 0508, fixed frontier $FB96.
JP/decomp/analysis/RESUME_STATE.json not modified.

**Next core decomp task:** reconcile PRG31 vector entrypoints with
the existing 0501 certified CFG, then return to mapper-grounded
classification at $FB96, promoting only independently justified spans.
