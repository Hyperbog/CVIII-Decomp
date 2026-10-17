# Checkpoint 04FE — fixed `PRG31:$E7FB` first-level inline dispatch

This checkpoint resumes from the committed 04FD switchable-bank -> fixed-PRG31 handoff and resolves the fixed side of the `$E7FB` inline dispatcher far enough to establish its calling convention, its first-level table, a strict fixed-code ZP `$10` audit, and the next nested semantic frontier.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery

The 04FD recovery overlap `raw bank $05:$BEC6-$BF05` and the fixed `PRG31:$E7FB-$E81A` fingerprint reproduce exactly. The previous bank-$05 audit also remains consistent: 72/72 bank-$05 roots are closed.

## `$E7FB` calling convention

The exact fixed code at `$E7FB-$E813` is:

```asm
E7FB  ASL A
E7FC  STY $03
E7FE  TAY
E7FF  INY
E800  PLA
E801  STA $00
E803  PLA
E804  STA $01
E806  LDA ($00),Y
E808  STA $02
E80A  INY
E80B  LDA ($00),Y
E80D  LDY $03
E80F  STA $03
E811  JMP ($0002)
```

SHA-256 of these 25 bytes:

```text
d2adbf45aa9746eb53ba2e8ec8513cb338f8fd30f4bc3627074f186c14439091
```

The routine is a tail dispatcher. A `JSR $E7FB` pushes the address of the final JSR byte. `$E7FB` doubles A, converts it to Y, adds one, pops that JSR return address into `$00/$01`, reads a little-endian target from the caller's inline bytes, restores the caller's Y, and jumps through `$0002`.

Therefore the selected target bytes are at:

```text
return_address + 1 + 2*A
return_address + 2 + 2*A
```

`$E7FB` itself writes only ZP `$00-$03`; it cannot write or alias ZP `$10`.

## NMI first-level call

04F3 established:

```asm
E35C  INC $1B
E35E  LDA $18
E360  JSR $E7FB
```

The inline bytes at `$E363-$E382` encode 16 pointer pairs:

```text
00 -> E383
01 -> E436
02 -> E437
03 -> E449
04 -> F390
05 -> E459
06 -> E49B
07 -> E539
08 -> E50E
09 -> E516
0A -> E541
0B -> E549
0C -> E51E
0D -> E526
0E -> E52E
0F -> E531
```

Table SHA-256:

```text
def43bbd8730858236b66f0cbfebec9d050c05a29ab90db176a3a4b3da186089
```

Important boundary detail: 04F3 byte coverage ended at `$E365`, so pointer entry 01 straddles old/new accounting (`$E365=$36` was already counted; `$E366=$E4` is new). 04FE keeps that overlap explicit rather than re-counting `$E365`.

This 16-entry structural table does **not** by itself prove that live `$18` is bounded to `$00-$0F`. The producer domain remains open and no host-side selector clamp is inferred.

## First-level fixed graph

All 16 encoded targets were used as a conservative root set. Recursive official-6502 decoding follows fixed-bank branches, fixed JSR/JMP targets, and treats a nested `JSR $E7FB` as a tail-dispatch boundary rather than falling through into inline data.

Result:

```text
fixed instruction starts: 435
unknown opcodes:           0
nested E7FB call sites:    1 ($F39A)
external banked edges:     21
```

The fixed graph contains no direct store/RMW to ZP `$10`.

The only reachable indexed zero-page writes requiring alias reconciliation are:

```asm
E7BA  STA $00,X
E7F3  STA $F0,X
E82A  STA $00,X
E82E  INC $01,X
```

Their X domains are ROM-bounded:

- `$E7B2` enters the `$E7BA` loop with X=`$28`; `$E7B6` enters with X=`$4D`; both stop at X=`$E0`, so the writes cover `$28-$DF` / `$4D-$DF`, never `$10`.
- `$E7F0-$E7FA` sets X=`$00` and loops while X `< $08`, so `$E7F3` touches only `$F0-$F7`.
- all reachable calls to `$E827` are `$EBAB`, `$EBD4`, `$EBEE`; `$EBA7` establishes X=`$00` and no intervening instruction changes X, so `$E827` touches only `$00/$01`.

Thus the resolved first-level **fixed** graph preserves ZP `$10`. This does not yet close its banked targets.

## Deferred external banked edges

The strict fixed graph exposes 21 banked exits. They are recorded rather than assigned guessed mapper state:

```text
E21E -> 87AE   JSR
E258 -> 8850   JSR
E39C -> A9D5   JSR
E3EF -> 8A8A   JSR
E479 -> 8957   JSR
E4A9 -> 8ED0   JSR
E4DA -> 8A81   JSR
E505 -> 8EA0   JSR
E513 -> A38D   JMP
E51B -> A513   JMP
E523 -> AFA4   JMP
E52B -> B4CC   JMP
E536 -> BBEA   JMP
E53E -> 8974   JMP
E546 -> B195   JMP
E54E -> B7D2   JMP
E642 -> B69D   JSR
E715 -> 8F1E   JMP
E7AC -> 8FFC   JSR
EC5B -> 966F   JSR
F6D6 -> 84A0   JSR
```

Some are reached through already-audited fixed helpers; mapper-state resolution and banked-body closure are intentionally deferred rather than inferred from CPU address alone.

## Nested `$2C` dispatcher

First-level entry `$04` reaches `$F390`:

```asm
F390  JSR $F6AE
F393  LDA $2D
F395  BEQ $F398
F397  RTS
F398  LDA $2C
F39A  JSR $E7FB
```

The following `$F39D-$F3DC` bytes form 32 encoded pointer pairs:

```text
F3FC F402 F48D F531 F5A8 F5D2 F61D F62C
F965 F638 F511 F831 F839 F841 F841 F4E7
F849 F65B F652 F713 F739 F792 F7CF F653
F6EC F3F4 F6E4 F4FA F6F4 F6FE F3EC F3DD
```

SHA-256:

```text
81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f
```

`$F3DD` begins code (`A9 02`), so an index of 32 would interpret `$F3DD-$F3DE` as pointer `$02A9`. That establishes the structural table boundary, but is **not** a proof that live `$2C` is restricted to `$00-$1F`. The `$2C` producer domain and nested target graph remain open.

## Exact new-byte accounting

04FE counts only new fixed bytes actually decoded or deliberately probed, subtracting prior 04F3 `$E057-$E365` and 04F4 `$EC00-$EFFF` coverage.

```text
E366-E433   206
E436-E576   321
E62D-E631     5
E63D-E647    11
E710-E717     8
E7A7-E813   109
E827-E830    10
EB44-EB6A    39
EB82-EBF6   117
F390-F3DC    77
F6AE-F6E3    54
----------------
TOTAL       957 genuinely new bytes
```

Ordered-manifest SHA-256 (ranges concatenated in the order above):

```text
a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32
```

Reproducible audit: `tools/audit_nmi_fixed_e7fb_dispatch.py`.

## Result / remaining boundary

**04FE proves the `$E7FB` mechanism and its first-level fixed-bank graph preserve ZP `$10`. It does not yet prove complete pre-render preservation.**

Open work is now sharper:

1. prove the actual `$18` producer domain rather than assuming 16 entries imply `$00-$0F`;
2. resolve the nested `$2C` producer domain and target graph beginning after `$F39D-$F3DC`;
3. resolve the 21 banked exits under their actual mapper state;
4. only then reconsider the transitive NMI-helper VPP item.

VPP therefore remains **21/100**.

The next fixed semantic frontier is `$F3DD`. The 64-byte nested table `$F39D-$F3DC` is the verification overlap for the next checkpoint and must not be counted again.
