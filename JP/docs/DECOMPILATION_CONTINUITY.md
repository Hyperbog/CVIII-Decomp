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

If state is blocked/provisional, repair only the recorded boundary. Forward work begins only from committed `ready` state. Verification overlap never counts as new coverage.

Evidence order:

1. authoritative JP ROM bytes / observed JP execution;
2. reproducible ROM-backed audits, traces and native parity tests;
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

Primary metric: **VPP = 21/100**. This is an evidence rubric, not raw-byte coverage.

## Checkpoint rules

Each user `continue` means one bounded checkpoint, normally 500-5000 genuinely new ROM bytes. Preserve exact 6502/VRC6/shared-ZP semantics. Every consumed instruction/stream operand byte must be inside claimed coverage or explicit prior coverage. Never infer table bounds, producer domains, mapper state, or host defaults from shape alone.

Transaction order:

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
- **04FF:** fixed nested prefix `$F3DD-$F7FF` maps all local `$2C` producers reachable from in-prefix nested targets; transitive exits remain open.

Historical 04F7/04F8 operand-boundary repair is resolved. Variable-width instructions/streams remain closed only when every byte actually read is covered. Raw `$FF` is not a generic terminator.

## Raw-bank closures

Bank `$04`: **96/96 roots closed**. Final 04FA `$B1F0-$BE7D`, 3184 genuinely new bytes after prior probes.

Bank `$05`: **72/72 roots closed**:

```text
04FB $87AE-$9A6A   4797 new   19 roots
04FC $9A6B-$AD96   4908 new   25 roots
04FD $AD97-$BF05   4463 new   28 roots
```

All live bank-$05 `$E7` parameter domains index legitimate `$8430-$8443` entries and dispatch to audited `$8444`; no host-side `$842D` clamp is introduced.

## 04FE — fixed `$E7FB` dispatch

Exact dispatcher `$E7FB-$E813` consumes the caller's JSR return address, reads an A-indexed inline pointer, restores Y, and tail-jumps through `$0002`. It writes only `$00-$03`; model it as a non-local tail dispatcher, not a conventional returning C helper.

The NMI caller `$E35E: LDA $18 / $E360: JSR $E7FB` has a 16-entry table at `$E363-$E382`. A conservative decode of all 16 targets gives 435 fixed instruction starts, one nested `$E7FB` at `$F39A`, and 21 mapper-dependent banked exits. Fixed write-domain reconciliation proves this first-level fixed graph preserves `$10`.

Nested state `$04` reaches:

```asm
F390  JSR $F6AE
F393  LDA $2D
F395  BEQ $F398
F397  RTS
F398  LDA $2C
F39A  JSR $E7FB
```

The 32 inline pointers occupy `$F39D-$F3DC`; `$F3DD` is code. Table length is not treated as a `$2C` bound.

04FE exact new coverage: **957 bytes**, ordered-manifest SHA-256 `a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32`.

## 04FF — fixed nested `$2C` prefix

Authoritative dependency:

```text
PRG31 $F3DD-$F7FF
1059 bytes
SHA-256 72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6
```

04FE already counted `$F6AE-$F6E3` (54 bytes). Exact 04FF new coverage is therefore **1005 bytes**:

```text
$F3DD-$F6AD   721 bytes   SHA-256 371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852
$F6E4-$F7FF   284 bytes   SHA-256 6f3c519ae6a1965fc20722535001e4c08a84dfde4245cfa79b78a463c8df0ce6
ordered manifest SHA-256 257dfb57d710e3eb4ea9e4ff1d4d168901e65dc3afc7c1c6054c1c5d2548e51a
```

Twenty-six unique nested table targets start inside this prefix:

```text
F3DD F3EC F3F4 F3FC F402 F48D F4E7 F4FA
F511 F531 F5A8 F5D2 F61D F62C F638 F652
F653 F65B F6E4 F6EC F6F4 F6FE F713 F739
F792 F7CF
```

Remaining table target starts: `$F831,$F839,$F841,$F849,$F965`.

Conservative prefix graph:

```text
instruction starts                    401
unknown official opcodes                0
indexed/indirect zero-page writes       0
direct $2C writers                     16
deferred exits                         136
  JSR                                  124
  JMP                                    9
  branch                                 2
  fallthrough                            1
```

Explicit local `$2C` writers:

```text
F3FF INC    root 00
F443 INC    root 01
F486 STA    root 01       #$09 or #$13
F4BF INC    roots 01,02
F4CF STA    roots 01,02   #$0F
F4DC STA    roots 01,02   #$0A
F4F3 STA    root 0F       #$10
F5CF INC    root 04
F629 STA    root 06       #$07
F635 STA    root 07       #$01
F64F STA    root 09       #$02
F6FB INC    root 1C
F716 INC    root 13
F775 INC    root 14
F7B4 INC    root 15
F7DB STA    root 16       #$10
```

Every constant local store is in `$00-$1F`, and there is no local indexed/indirect ZP write that can hide a `$2C` alias. Root-associated INCs are also locally compatible with the table family. **Do not promote this to full producer closure:** any of the deferred callees may still mutate `$2C` until audited under actual mapper/context state.

Existing US CVIII labels (`ram_002A_script`, states `$00-$1F`) are useful secondary naming evidence only; JP bytes above remain controlling.

Evidence:

- `analysis/NMI_FIXED_2C_PREFIX.md`
- `tools/audit_nmi_fixed_nested_prefix.py`

## Open edges after 04FF

1. `$18` producer domain for the first-level NMI dispatch.
2. transitive `$2C` producer proof across 04FF deferred callees.
3. remaining nested target bodies starting at `$F831/$F839/$F841/$F849/$F965` and continuation beyond `$F800`.
4. mapper-dependent `$8000-$BFFF` exits; resolve actual VRC6 state before traversal.

## Current provenance boundary

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
nested fixed $F3DD-$F7FF              -> local $2C write-domain mapped
$18 selector producer domain          -> unresolved
full $2C producer/transitive graph     -> unresolved
mapper-dependent banked exits         -> unresolved
PRG26 renderer                        -> consumes/persists $10 exactly
```

VPP remains **21/100**.

## Next checkpoint: 0500

Start fixed PRG31 at **`$F800`**. Initial bounded interval:

```text
$F800-$FBFF
1024 contiguous bytes
```

Recovery overlap:

```text
$F7C0-$F7FF  64 bytes
SHA-256 0654eeccd284ba39d016f954cdfbe17b34b7218a1afe2bc6eca799a2713a13f7
```

Frontier fingerprint:

```text
$F800-$F81F  32 bytes
SHA-256 322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24
```

Requirements:

- continue through remaining nested target entries `$F831/$F839/$F841/$F849/$F965`;
- subtract all overlap with 04FE/04FF manifests;
- distinguish local `$2C` writers from mutations in called helpers;
- resolve actual mapper state before traversing `$8000-$BFFF` targets;
- do not infer `$18` or `$2C` bounds from table shape or US labels;
- preserve exact `$E7FB` stack/Y/ZP `$00-$03` behavior and shared `$10` semantics;
- update `RESUME_STATE.json` last.

User-facing handoff:

> Continue on branch `decompilation` using mandatory recovery first. Current target is checkpoint 0500 at fixed `PRG31:$F800`, with `$F7C0-$F7FF` as verification-only overlap. 04FF mapped the local `$2C` write-domain but did not assume its 136 deferred exits preserve `$2C` or `$10`. JP ROM evidence controls all bounds and mapper contexts.
