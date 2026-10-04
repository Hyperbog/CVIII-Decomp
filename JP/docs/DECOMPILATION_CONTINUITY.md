# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Mandatory recovery

After any interruption:

1. read `docs/INTERRUPTION_RECOVERY.md`;
2. read `docs/ACCELERATION_POLICY.md`;
3. read `docs/WHOLE_PRG_ATLAS.md`;
4. read `analysis/RESUME_STATE.json`;
5. run `python tools/check_resume_frontier.py <authoritative JP ROM.nes>`;
6. run the previous checkpoint audit against the same ROM;
7. only then continue semantic work.

Evidence order: JP ROM / observed JP execution -> reproducible ROM-backed audits -> NES/VRC6 hardware docs -> atlas/external disassemblies/CDL/Ghidra/decompilers as accelerators.

Never commit the ROM or lossless generated PRG listings.

Target ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

VPP: **21/100**.

## Stable closed provenance

```text
IRQ graph                              -> preserves $10
fixed NMI $E057-$E365                 -> preserves $10
$ED46 fixed helper graph              -> preserves $10
raw bank $0C / PRG24                  -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots     -> preserves $10
raw bank $05 parser + 72/72 roots     -> preserves $10
$E7FB + first-level fixed graph        -> preserves $10
04FF nested $2C fixed head             -> preserves $10
0500 secondary $68 fixed graph         -> preserves $10 locally
PRG26 renderer                         -> consumes/persists $10 exactly
```

Open transitive edges remain `$18`, full `$2C`, full `$68`, and mapper-dependent callees.

## Whole-PRG acceleration

Use these before narrow ROM searching:

```text
tools/build_whole_prg_atlas.py
tools/query_whole_prg_atlas.py
tools/audit_whole_prg_atlas.py
analysis/WHOLE_PRG_ATLAS_MANIFEST.json
analysis/WHOLE_PRG_FOCUS_SUMMARY.md
```

Large discovery sweeps may cover the full PRG, but candidate decodes do not become verified coverage automatically.

## Fixed dispatcher chain

### 04FE

`$E7FB-$E813` is a stack-return-address tail dispatcher. NMI `$E35E: LDA $18 / $E360: JSR $E7FB` uses inline pointer data. Nested state `$04` reaches `$F390`, loads `$2C`, and dispatches through 32 pointer pairs at `$F39D-$F3DC`.

04FE: 957 new bytes, manifest SHA:
`a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32`.

### 04FF

04FF admitted 26 nested `$2C` roots in `$F3DD-$F7FF`: 401 instruction starts, 931 genuinely new bytes, manifest SHA:
`2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4`.

It left four gaps unclaimed and handed an explicit fallthrough boundary at `$F800` to 0500.

### 0500 — corrected controlling result

Deferred primary entries:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

Required roots are:

```text
F800 F831 F839 F841 F849 F965
```

`$F849: LDA $68 / JSR $E7FB` uses 16 pointers at `$F84E-$F86D`; entries `$0C-$0F` target `$F706/$F724/$F782/$F7B7`, admitting all four former 04FF gaps.

`$F965: LDA $68 / JSR $E7FB` uses 10 pointers at `$F96A-$F97D`.

No table size is a live selector bound.

Correct 0500 result:

```text
instruction starts                 414
reachable store/RMW instructions    82
indexed write/RMW forms              9
ZP $10 aliases                       0
genuinely new semantic bytes       982
```

Exact manifest:

```text
F706-F712    13   8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025
F724-F738    21   41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e
F782-F791    16   17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b
F7B7-F7CE    24   0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be
F800-FA9F   672   6dea651f93c64d59355c4180907677d367bb705ed84cbfa6ec59da79009028a8
FAAA-FB95   236   5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402
```

Ordered SHA:
`fdc1a53db0ee18ca5e70188d2c8b31d1b350c91d011f72fddb4b6fcb7434984e`.

The earlier 933-byte 0500 draft is invalid because it omitted the `$F800` root.

`$FB31-$FB36` is a proven six-byte ROM record. `$FAA0-$FAA9` remains unclaimed until `$62/$054E` index domains are proven.

Verified `$2C` mutations in 0500:
`$F736,$F78F,$F7CC,$F962,$FB77`.

Verified `$68` mutations:
`$F706,$F72F,$F78D,$F874,$F896,$F8AE,$F8E6,$F916,$F957,$F9B4,$F9D0,$F9FC,$F9FF,$FAB7,$FAD7,$FB04`.

Controlling evidence:

```text
analysis/NMI_FIXED_68_DISPATCH.md
tools/audit_nmi_fixed_68_dispatch.py
```

## Next checkpoint — 0501

Resume fixed PRG31 at `$FB96`.

```text
$FB96-$FFFF   1130 raw bytes
SHA-256       0cbfd0aa79f3c7d1db7a756c08c47bfe01cba321900fb8955e77ec8525d38d44

overlap $FB76-$FB95
SHA-256       e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7

fingerprint $FB96-$FBB5
SHA-256       a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157
```

Only unclaimed bytes below the raw frontier: `$FAA0-$FAA9` (10).

0501 priorities:

1. whole-atlas query first;
2. sweep `$FB96-$FFFF`;
3. classify `$FE95: JSR $E7FB` from actual control flow and inline data;
4. reconcile exact ROM-data dependencies;
5. continue `$18/$2C/$68` producer/alias closure;
6. traverse `$8000-$DFFF` callees only with proven VRC6 mapper state.

Checkpoint order remains: analysis -> audit -> exact-ROM run -> progress/continuity -> `RESUME_STATE.json` last -> recovery checker -> branch-head confirmation.
