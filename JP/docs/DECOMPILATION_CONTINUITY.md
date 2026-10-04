# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Mandatory interruption recovery

After any timeout, thread/token limit, crash, model/context switch, long pause, or uncertain partial checkpoint, do **not** resume from chat memory.

Read:

- `docs/INTERRUPTION_RECOVERY.md`
- `docs/ACCELERATION_POLICY.md`
- `analysis/RESUME_STATE.json`

Then run:

```text
python tools/check_resume_frontier.py <authoritative JP ROM.nes>
```

If the state is blocked/provisional, repair only the recorded boundary. Forward work starts only from a committed `ready` state. Verification overlap never counts as new coverage.

Evidence order:

1. authoritative JP ROM bytes / observed JP execution;
2. reproducible ROM-backed audits, traces, native parity tests;
3. NES hardware documentation;
4. external disassemblies, CDL, Ghidra, retrodisasm, decompilers, nesrecomp, NSF metadata and JP↔US matching as accelerators;
5. semantic labels remain provisional until JP reconciliation.

Never commit the ROM.

Target:

```text
size       393232 / 0x60010
SHA-256    958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
PRG        256 KiB, CRC32 BA6BDD6A
CHR        128 KiB, CRC32 BF15255C
mapper     24 / Konami VRC6a
```

Primary metric: **VPP = 21/100**. This is an evidence rubric, not raw byte coverage.

## Checkpoint rules

Each user `continue` means one bounded checkpoint, normally 500-5000 genuinely new ROM bytes. Preserve exact 6502/VRC6/shared-ZP semantics. Every consumed instruction/stream operand byte must be inside claimed coverage or explicit prior coverage. Never infer table bounds, producer domains, mapper state, or host defaults from shape alone.

Checkpoint transaction order:

1. analysis/evidence;
2. audit tool;
3. run audit against exact ROM;
4. progress + continuity;
5. `analysis/RESUME_STATE.json` **last**;
6. run recovery checker and confirm branch head.

## Stable hardware / renderer facts

VRC6 windows:

```text
$6000-$7FFF PRG RAM
$8000-$BFFF switchable 16 KiB PRG
$C000-$DFFF switchable 8 KiB PRG
$E000-$FFFF fixed PRG31
```

Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.

NMI bank `$0D` call `$8001` = `PRG26:$8001`. IRQ raw bank `$01` = PRG02/03; exact IRQ table is `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`; `$9F5B` is code and `$80` is the high-bit bypass.

`PRG26:$8001` iterates 28 render slots. Full descriptors are `Y,tile,attribute,X`; compressed descriptors are `Y,tile,X` and consume persistent shared ZP `$10`. Full records update `$10`; compressed records consume it unchanged. Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

## Pre-render `$10` provenance history

- **04F2:** IRQ graph preserves `$10`.
- **04F3:** fixed NMI `$E057-$E365` preserves `$10`; external dependencies found.
- **04F4:** `$ED46` fixed helper graph preserves `$10`.
- **04F5-04F6:** raw bank `$0C` live graph preserves `$10`; `$842D` proved unreachable there.
- **04F7-04FA:** bank `$04` parser and all **96/96 roots** preserve `$10`.
- **04FB-04FD:** bank `$05` parser and all **72/72 roots** preserve `$10`, including ROM-proven live `$E7` producer domains.
- **04FE:** `$E7FB` mechanism and conservative first-level fixed target graph preserve `$10`; nested selector and banked exits remain open.

Historical 04F7/04F8 operand-boundary repair is resolved. The important invariant remains: a variable-width opcode is not closed unless every operand it reads is accounted. Raw `$FF` is not a generic sound-stream terminator.

## Raw-bank closures

Bank `$04`: 96/96 roots closed. Final 04FA `$B1F0-$BE7D`, 3184 genuinely new bytes after prior probes.

Bank `$05`: 72/72 roots closed:

```text
04FB $87AE-$9A6A   4797 new   19 roots
04FC $9A6B-$AD96   4908 new   25 roots
04FD $AD97-$BF05   4463 new   28 roots
```

All live bank-$05 `$E7` parameter domains index legitimate `$8430-$8443` entries and dispatch to audited `$8444`; no host-side `$842D` clamp is introduced.

## 04FE — fixed `$E7FB` first-level dispatch

Exact dispatcher `$E7FB-$E813`:

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

It is a tail dispatcher over pointer data immediately after the caller's `JSR`. It writes only `$00-$03` and does not return normally.

The NMI caller is `$E35E: LDA $18 / $E360: JSR $E7FB`. Inline table `$E363-$E382` contains 16 encoded targets:

```text
E383 E436 E437 E449 F390 E459 E49B E539
E50E E516 E541 E549 E51E E526 E52E E531
```

A conservative recursive decode from all 16 targets yields 435 fixed instruction starts, zero unknown opcodes, one nested `$E7FB` site at `$F39A`, and 21 mapper-dependent banked exits. No reachable fixed write can alias `$10` after X-domain reconciliation.

### Nested dispatcher

First-level target `$F390` executes:

```asm
F390  JSR $F6AE
F393  LDA $2D
F395  BEQ $F398
F397  RTS
F398  LDA $2C
F39A  JSR $E7FB
```

Its 32 encoded pointer pairs occupy `$F39D-$F3DC`:

```text
F3FC F402 F48D F531 F5A8 F5D2 F61D F62C
F965 F638 F511 F831 F839 F841 F841 F4E7
F849 F65B F652 F713 F739 F792 F7CF F653
F6EC F3F4 F6E4 F4FA F6F4 F6FE F3EC F3DD
```

`$F3DD` starts code (`A9 02`). This establishes the table's structural boundary but **does not prove** live `$2C` is `$00-$1F`. Likewise the 16 first-level entries do not prove live `$18` is `$00-$0F`.

### Exact 04FE coverage

04FE contributes **957 genuinely new fixed PRG31 bytes** in this noncontiguous manifest:

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
```

Ordered-manifest SHA-256:

```text
a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32
```

Evidence:

- `analysis/NMI_FIXED_E7FB_DISPATCH.md`
- `tools/audit_nmi_fixed_e7fb_dispatch.py`

## Open edges after 04FE

1. `$18` producer domain for the first-level NMI dispatch.
2. `$2C` producer domain and nested target graph beginning at fixed `$F3DD`.
3. 21 `$8000-$BFFF` exits from the fixed graph; resolve actual mapper state before traversing them.

Do not count any 04FE manifest byte twice when later nested targets overlap already audited fixed ranges.

## Current provenance boundary

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
$18 selector producer domain          -> unresolved
nested $2C selector/targets           -> unresolved
21 mapper-dependent banked exits      -> unresolved
PRG26 renderer                        -> consumes/persists $10 exactly
```

VPP remains **21/100**.

## Next checkpoint: 04FF

Start fixed PRG31 at **`$F3DD`**. Initial bounded interval:

```text
$F3DD-$F7FF
1059 contiguous bytes
```

Recovery overlap:

```text
$F39D-$F3DC  64 bytes
SHA-256 81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f
```

Frontier fingerprint:

```text
$F3DD-$F3FC  32 bytes
SHA-256 65d47f163ffad5ca20903cece8606c76416ceb5cb8edba99780be720730f08aa
```

Requirements:

- treat `$F39D-$F3DC` as inline pointer data, not executable fall-through;
- prove `$2C` producer values from JP-ROM producer/control flow before claiming table bounds;
- recursively close only actually admitted nested targets;
- reuse 04FE noncontiguous manifest bytes as prior coverage;
- resolve mapper state before traversing any `$8000-$BFFF` edge;
- preserve exact stack/flag/ZP behavior of `$E7FB` tail dispatch;
- update `RESUME_STATE.json` last.

User-facing handoff:

> Continue on branch `decompilation` using mandatory recovery first. Current checkpoint target is 04FF at fixed `PRG31:$F3DD`, with `$F39D-$F3DC` as verification-only overlap. Resolve the actual `$2C` selector domain/nested graph and reuse 04FE manifest ranges rather than recounting them. JP ROM evidence controls all external labels and bounds.
