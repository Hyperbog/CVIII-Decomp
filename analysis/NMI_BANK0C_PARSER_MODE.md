# Checkpoint 04F6 — bank `$0C` parser-mode closure

This checkpoint revisits the one open edge left by 04F5: PRG24 `$842D`, an indirect dispatch reached by the alternate sound-stream parser after command `$E7` sets a transient state bit.

The original 04F5 static graph was deliberately conservative: it seeded `$842D` without carrying two pieces of machine state that decide whether PRG24 can actually execute that edge:

1. the current instrument-data bank;
2. bit 0 of the per-instrument parser-control byte at `$011B,X`.

The JP ROM proves that this edge is not live for bank `$0C` stream data.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

New ROM span added by this checkpoint:

```text
physical PRG24 / CPU $9200-$9FFF
3584 bytes
SHA-256 d7387b04a03289ebb1a0567ef49240d90b0bb177a0c128c8b06dbccabdb0776f
```

Earlier 04F5 code span `$8000-$91FF` is reused rather than recounted.

## Parser selection is stateful

Fixed helper `$E1AF` selects the current instrument-data bank from `$06D3,X` and then jumps to CPU `$8001`:

```asm
E1AF  BD D3 06   LDA $06D3,X
E1B2  20 D0 E2   JSR $E2D0
E1B5  4C 01 80   JMP $8001
```

Thus CPU `$8001` executes from whichever raw 16 KiB bank owns the instrument stream.

When execution is in raw bank `$0C`, PRG24 `$8DCD` selects the next parser from bit 0 of `$011B,X`:

```asm
8DCD  4A         LSR A
8DCE  90 03      BCC $8DD3
8DD0  4C EA 8D   JMP $8DEA   ; main parser
8DD3  4C AF E1   JMP $E1AF   ; alternate parser at instrument-data bank
```

So a static PRG24 control-flow graph that seeds both parsers without this bit over-approximates runtime reachability.

## Mode-bit initialization

During sound metadata installation, the first instrument byte is read through `$E19F`. The JP code at `$88E0-$88F4` then computes `$011B,X` bit 0:

```asm
88E0  JSR $E19F
88E3  INY
88E4  CMP #$10
88E6  BCC $88F1
88E8  CPX #$05
88EA  BEQ $88F1
88EC  CPX #$06
88EE  BEQ $88F1
88F0  DEY
88F1  TYA
88F2  STA $011B,X
```

Therefore:

```text
main parser (bit0=1): first byte < $10, or instrument $05/$06
alternate parser (bit0=0): otherwise
```

## Bit 0 remains stable

A complete raw-bank `$0C` inventory contains 17 direct `STA $011B,X` sites.

- `$88F2` is the initializer above.
- Every other site is a read/modify/write sequence whose `AND`/`ORA` mask preserves bit 0.
- There is no direct absolute, absolute-Y, RMW, STX, or STY writer to `$011B` in the raw bank pair.

Representative transforms include:

```text
(old & $BB) | $02
old & $B9
old | $40
old & $F7
old & $FB
old | $08
old | $20
old & $DF
old & $F9
old | $06
(old | $04) & $FD
old | $80
old & $7F
```

All leave bit 0 unchanged. Parser mode is therefore not silently changed later by these sound-engine control handlers.

## Exact bank-$0C metadata domain

The JP sound metadata pointer table is exactly 125 sound IDs at `$8F60-$9059`; the first metadata record starts immediately at `$905A`.

Parsing the records yields:

```text
bank-$0C instrument references: 139
distinct bank-$0C stream roots: 125
```

Applying the ROM's own parser-mode rule leaves exactly five alternate-parser references:

```text
sound $0C, instrument $08 -> $9D8F
sound $0D, instrument $08 -> $9F73
sound $22, instrument $08 -> $A303
sound $3A, instrument $08 -> $A303
sound $3B, instrument $08 -> $A303
```

All three distinct roots begin with `$FF`.

The bank-$0C streams that contain raw byte `$E7` are instead rooted at `$9688`, `$97B7`, `$97C2`, and `$9D6F`; every one initializes with first byte `$01`, hence main-parser mode. Those `$E7` bytes do not feed PRG24 `$8418/$842D`.

## Correction to the 04F5 boundary

04F5 correctly proved that the statically closed PRG24 graph has no write form capable of aliasing ZP `$10`, but it left `$842D` open because the local table has only ten entries and no local bounds check.

The missing fact was not a hidden table bound. It was **bank + parser-mode reachability**.

For raw bank `$0C`:

```text
live non-terminating streams -> main parser
alternate-parser roots       -> $FF termination roots
PRG24 $842D                   -> not a live bank-$0C stream edge
```

Therefore the earlier request to prove an `$E7` parameter domain from PRG24 `$9200-$9FFF` was targeting an unreachable local edge.

This does **not** prove that copies of the alternate parser in other instrument-data banks are irrelevant. `$E1AF` deliberately switches to the instrument-data bank before entering `$8001`. Those banks must be audited separately if they are reachable during the pre-render sound update.

## Result

**04F6 closes PRG24/bank `$0C` `$842D` as a state/bank over-approximation.**

The remaining sound-side pre-render `$10` question moves to the other instrument-data banks selected by `$06D3,X`, not to additional PRG24 stream-byte scanning.

Reproducible audit: `tools/audit_nmi_bank0c_parser_mode.py`.
