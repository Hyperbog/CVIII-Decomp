# Checkpoint 0501 — fixed scheduler tail + proven mapper-selected callees

0501 is a large semantic checkpoint using the whole-PRG atlas workflow. It begins from the corrected 0500 raw fixed-bank frontier `$FB96`, but it does **not** claim the entire physical `$FB96-$FFFF` tail by contiguity. Instead it follows the first verified inbound root `$FDE4`, then admits mapper-selected banked callees only where the fixed scheduler itself proves the VRC6 bank.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Result summary

```text
fixed PRG31 graph                161 instruction starts
new fixed semantic bytes         298

raw bank $09 graph               479 instruction starts
new raw-$09 semantic bytes      1050

raw bank $0A graph                57 instruction starts
new raw-$0A semantic bytes       120

raw bank $0B graph              1338 instruction starts
new raw-$0B semantic bytes      2896
------------------------------------
0501 exact new tracked bytes    4364
```

Tagged ordered-manifest SHA-256:

```text
639e20f7e96e816a40ef4ef7d8585c809ce670ac5384f3c2fabc9a77d275737e
```

The tracked PRG lower bound therefore advances from `44,457` to **48,821 bytes**, or **18.6237% of the 256 KiB PRG**. This remains a conservative semantic floor, not a claim that only 18.6% of the ROM has been inspected.

## Fixed scheduler root and mapper contexts

Corrected 0500 hands an explicit fixed edge to `$FDE4`. The scheduler begins:

```asm
FDE4  INC $A0
FDE6  LDA #$FF
FDE8  STA $8F
FDEA  LDX #$01
...
FDF3  LDA #$0B
FDF5  JSR $E2D0
FDF8  JSR $80E3
FDFB  JSR $B1F8
```

The admitted fixed graph contains 161 official instruction starts, no unknown opcodes, no zero-page-indexed/indirect writes, and no direct write/RMW to `$10`.

Exact genuinely-new fixed coverage:

```text
FDE4-FEE9   262  87cb2d7b62449573311d9a9aae13cdb072d3058d42faf82b9c7b81c5b6e3a3c1
FF56-FF79    36  3bc8a1cf86ea269287fe1133f416880d9c552654d537ab02676a968c4737124d
```

Total: **298 bytes**.

The scheduler explicitly establishes these banked roots:

```text
raw $0B  $80E3
raw $0B  $B1F8
raw $0B  $BD11        (bank remains $0B across the admitted B1F8 graph)
raw $09  $8001
raw $0B  $8001
raw $0B  $8161
raw $0B  $826C
raw $0A  $84EA
```

No CPU `$8000-$BFFF` target is traversed under guessed mapper state.

## `$FE95` inline dispatcher

The fixed state helper at `$FE8C` is real code:

```asm
FE8C  LDA $0565,X
FE8F  LSR A
FE90  LSR A
FE91  LSR A
FE92  LSR A
FE93  LSR A
FE94  LSR A
FE95  JSR $E7FB
```

Bytes `$FE98-$FE9D` are exactly three encoded pointers:

```text
00 -> $FE9E
01 -> $FEB1
02 -> $FEC6
```

`$FE9E` begins executable code (`LDA #$80`), so `$FE9E-$FE9F` must **not** be swallowed as a fictitious fourth pointer.

The shift expression can arithmetically produce `$00-$03`, but 0501 does **not** infer that selector `$03` is live or impossible solely from table shape. The producer domain for the high two bits of `$0565,X` remains an explicit open edge.

## Raw bank `$09`

The scheduler selects raw bank `$09` immediately before `$8001`.

Strict local graph:

```text
instruction starts   479
semantic code bytes 1050
direct ZP $10 writes 0
ZP indexed aliases   0
```

Exact ranges:

```text
8001-814F   335  2dd7d61df700b59351a3233b09df098f97f6c338828e74a54b349a0136006bc7
8152-8162    17  52202e6406418453ccc7e56bf3eb725fd468e4f59b0cef10017baa06c1159b47
8250-831E   207  9d1b0adbc05522dcbf64c234e41a96db047d86f35eec0f3bd35c5537705fdf7b
8357-8419   195  6e4880f156a25ec9cc3629d85b02345b115a2f0899f6d92f1b062d7b474d3560
843C-84E4   169  18b0aeae2ef5979d33e052059c6dc827bd086f7588d6dc80e888e9e6d8eb9281
8692-86BD    44  23f97b589e7577cb68385e24c313f013774a71c74df7339ef207b0def906155c
8810-8862    83  9cb9e1a5b221e5de3749feb2c2a45d9a141cd31bfcd6bba2d9b03bdf2d1d8b38
```

This proves the admitted raw-$09 code itself is `$10`-clean. It does **not** yet close the indirect `$E5DA` temporary-bank callees.

## Raw bank `$0A`

The fixed scheduler selects raw bank `$0A` immediately before `$84EA`.

Strict local graph:

```text
instruction starts    57
semantic code bytes  120
direct ZP $10 writes  0
ZP indexed aliases    0
```

Exact ranges:

```text
83D1-840F    63  f302ac2b3ac985520f5d7780d6583a5cbed3f9164b33136484b157b2c99f4a90
84EA-8522    57  5190ad255e8121db4a4c4143c7965f0a5391391465e46618a39e9644fa992bfb
```

The admitted raw-$0A graph is locally `$10`-clean.

## Raw bank `$0B`

The fixed scheduler explicitly selects raw bank `$0B` for the object/collision path. The admitted roots are:

```text
$80E3
$B1F8
$BD11
$8001
$8161
$826C
```

The graph has:

```text
instruction starts   1338
semantic code bytes  2896
zero invalid decodes
zero ZP indexed/indirect write aliases
```

The only mapper-changing helper used inside the admitted raw-$0B graph is fixed `$E249`, at `$A331/$B4BE/$B4DC/$B53C`. `$E249` saves the current bank, temporarily selects raw bank `$0C`, performs its helper call, and restores the saved bank. Therefore the caller's raw-bank `$0B` context is stable across those calls.

`$B96E: CMP #$10` is followed by `BCS $B96D` and then `BCC $B95D`; those complementary branches exhaust the carry outcomes from the same compare. The apparent raw fallthrough at `$B974` is therefore not executable from this graph and is not decoded as code.

Exact raw-$0B ranges:

```text
8001-804A    74  4f8acdadcc27a00278b799ca271122d46c05473d92f19e1f01ee505113fccef9
80B3-821A   360  8808b66fc5d79e67731f93e6b1fa6554d72262b9e5b29a1e4867ae2758c32ca7
8253-8290    62  970aa4064d4764e045bf51afb40cb64e7dcafa6fc65778db3e3bbc24555c3930
82CD-82EE    34  1222fb43b483c3a0f3e1e2ad973cec228fc29f60a550d50bd0141d789fe92a75
8309-8311     9  ac7aded349ec49398a679d2da45eecb298b89b4581671c895599bd61768dd6ae
8315-831D     9  25de7e8be3bee10543ef719c350ff4317d161faf3cc3e1709eb0c10716ae0be3
8843-886B    41  c79cb2d2295368c2034f93615d0acf4aca20a24c3a338c9f3be0f7d54854d8eb
A154-A15C     9  b2bac4515e62017992e1cd8ff89a0a307871a8b8503a68f3d74625e5ac769cae
A2C9-A2CE     6  f79e1d0981d284dfb551be33010685836f73901c76db0e97145bf45fa42feca1
A329-A365    61  6825e459291b646417e7f1d918677e7f76453379a1560ae24fc933fd79485c2a
A3A6-A3AB     6  b0098751a43af502824e9ac33341c0384a53559d6fcef54360b23682f2107adc
B106-B31F   538  ffbbafe28471a79bdb0f4b7b08b11a27ce8ce47ced545dbed205560658dc8f48
B323-B393   113  ada777e3c5d6cff781f04cd8c1afdc4afedc27aa589d4ece91060189f8a618a5
B396-B4D4   319  0356b104267a70383b750c09187209c282e7dd252fb518f11b56f65341c6b167
B4D7-B628   338  d6ca1dcb716862996f99c2253f005b202eab7224e8dd6666c8cbbf1d2dae3e03
B632-B672    65  efee106fa7f7651f999d6110514425dc8615da42f47de108b57a056224a807e0
B6CE-B781   180  cb72dbf7c191a568d7fc61498a7b3a0038a16594fdc1767d8f56d6b9710927fd
B7E5-B973   399  ef24909ade0b6e170c013403a7ba513f84d8109496bbcd17ddb47b70872cb896
B986-BA3F   186  8a4c0047b50f6b7b7c8b843928334e6dd8197baff8ec7669c5939ce12b281559
BD10-BD66    87  d4336919aa9623d6a468541ba5f578dc8127d494a781af95811994bec2eb04b9
```

### The important `$10` result

Unlike raw banks `$09/$0A`, raw bank `$0B` does **not** preserve shared zero-page `$10`.

The admitted graph contains exactly seven direct stores:

```text
$B3B6  STA $10
$B3D2  STA $10
$B40E  STA $10
$B460  STA $10
$B65F  STA $10
$B740  STA $10
$B76C  STA $10
```

These are real control-flow-reachable writes in the scheduler-selected raw-$0B domain, not atlas byte-pattern candidates.

The surrounding code shows `$10/$11` being used as coordinate scratch pairs in collision/position calculations. Therefore the previous provenance question must be reframed: `$10` is not simply preserved from earlier NMI work; raw-$0B collision/object processing can intentionally replace it before the renderer later consumes its inherited value.

0501 does **not** yet claim which of the seven sites is the final writer on every live frame/object path.

## Open edges

0501 deliberately leaves these unresolved:

1. high-two-bit producer domain of `$0565,X` at `$FE95` (three encoded pointers; arithmetic selector `$00-$03`);
2. raw-$09 indirect/E5DA-selected callees and their `$10` behavior;
3. raw-$0B `$E7FB` dispatch sites at `$A15A/$A2CC/$A3A9`;
4. raw-$0B indirect jumps at `$BD56/$BD64`;
5. fixed helper-selected banked callees beyond the local 0501 budget;
6. exact final-writer/value domain for the seven raw-$0B `$10` stores;
7. first-level `$18`, full `$2C`, and full `$68` producer closure remain open;
8. `$FAA0-$FAA9` remains unclaimed pending `$62/$054E` index-domain proof.

## Evidence

Reproducible audit:

```text
tools/audit_nmi_fixed_scheduler_banked.py
```

This checkpoint changes the provenance model from “all discovered predecessors preserve `$10`” to the stronger and more accurate statement:

```text
earlier NMI/audio domains        -> preserve $10
fixed scheduler local graph      -> preserves $10
raw bank $09 local graph         -> preserves $10
raw bank $0A local graph         -> preserves $10
raw bank $0B object/collision    -> intentionally WRITES $10 at 7 verified sites
renderer                         -> consumes/persists inherited $10
```

VPP remains 21/100 until the final writer/value domain and remaining mapper/selector edges are closed.
