# Whole-PRG atlas — focused producer/xref snapshot

This is a compact derived snapshot from `tools/build_whole_prg_atlas.py`. It is an aggressive byte-offset scan, **not verified code/data classification**. Use it to shortlist locations; promote only after JP-ROM control-flow / mapper-context proof.

Authoritative ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

Whole-PRG candidate totals:

```text
official-opcode candidates     186258
control-flow candidates        110127
memory-access candidates        87686
zero-page write candidates      17841
raw JSR $E7FB byte patterns        35
```

Focused raw candidate-reference counts:

```text
$10  534
$18  311
$2C  119
$68  185
```

Writer/RMW candidate totals among those focused variables:

```text
$10  202
$18  100
$2C   65
$68  113
```

## Fixed PRG31 write/RMW shortlist

These fixed-bank candidates are immediately useful to the current 0500 producer-domain work.

### `$10`

```text
E8E3 E951 E975 E9DE EA65 EA87 EAA1 EAC2
FBFC FC17 FC1F FC4F FCA0 FCF9
```

### `$18`

```text
E48F E551 E558 F137 F184
```

### `$2C`

```text
E44B E493
F3AA F3FF F443 F486 F4BF F4CF F4DC F4F3
F5CF F629 F635 F64F F6FB F716 F736 F775
F78F F7B4 F7CC F7DB F962 FB77
```

### `$68`

```text
E401 E442 E4D0 E4EC E5EC E5FE E6AE
F4F7 F504 F6F6 F706 F72F F78D F7DF
F874 F896 F8AE F8E6 F916 F957 F9B4 F9D0
F9FC F9FF FAB7 FAD7 FB04
```

Several entries above are already known verified instructions from 04FE/04FF. Others are only candidate decodes until reached by valid control flow. In particular, the scan immediately highlights `$F962`/`$FB77` as later `$2C` write candidates and the dense `$F874-$FB04` `$68` mutation region relevant to 0500.

## Exact raw `20 FB E7` pattern locations

The whole PRG contains 35 exact byte-pattern candidates for `JSR $E7FB`:

```text
PRG00 +10F5 +12BF +12E0 +1BB2
PRG01 +038F +11CF +17DB +18AF
PRG03 +051E +1197 +17D4
PRG06 +199B +1A07 +1CDA
PRG21 +0FA6 +1122 +14CE +168B
PRG22 +0555
PRG23 +015A +02CC +03A9 +03B9 +03C7 +03D5 +03E3
PRG25 +0BB5 +1BEC +1C35
PRG28 +0AE3
PRG31 +0360 +139A +184B +1967 +1E95
```

For PRG31 the fixed CPU addresses are:

```text
E360 F39A F84B F967 FE95
```

`E360`, `F39A`, `F84B`, and `F967` are already implicated by the current NMI/gameplay dispatch analysis. `FE95` is now an explicit whole-ROM candidate to classify rather than rediscover later.

For non-fixed physical banks, canonical raw16 and possible `$C000` views must still be reconciled under actual VRC6 mapper state before semantic traversal.

## Use

The compact snapshot is deliberately incomplete compared with the generated local TSV database. Regenerate the full atlas when arbitrary RAM addresses, control targets, or all candidate memory accesses are needed:

```text
python tools/build_whole_prg_atlas.py ROM.nes OUTDIR
python tools/query_whole_prg_atlas.py OUTDIR ram '$2C' --writes-only
```

The generated lossless bank `.asm` files remain local-only because committing them would be equivalent to committing ROM contents.
