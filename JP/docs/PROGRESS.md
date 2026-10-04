# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md` and `analysis/RESUME_STATE.json` and run `tools/check_resume_frontier.py` before forward work.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

Checkpoint **04FA closes the entire raw-bank `$04` sound-stream producer domain: 96/96 roots are now reconciled and ZP `$10`-safe.** The next sound-side domain is raw instrument bank `$05` / physical PRG10-PRG11.

## Stable foundation

- Exact Japanese `Akumajou Densetsu` Mapper-24/VRC6a ROM identity is locked.
- PRG is modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG bank helpers and fixed/switchable contexts are mapped.
- NMI bank `$0D` call `$8001` resolves to `PRG26:$8001`.
- IRQ raw bank `$01` resolves into `PRG02/PRG03`.

## IRQ / OAM stable results

`PRG02:$9F01-$9F5A` is the exact 45-entry IRQ table for states `$00-$2C`; `$9F5B` is code. `$80` is the high-bit bypass sentinel. `$E118` clears IRQ Control before acknowledge; `$E11D` enters at acknowledge without that clear.

`PRG26:$8001` iterates 28 render slots. Sprite descriptors are full `Y,tile,attribute,X` or compressed `Y,tile,X`; compressed records consume persistent shared ZP `$10`, while full records update it. `$9FA9` is normally reachable and can begin with compressed records, so pre-render `$10` provenance matters.

Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

## Pre-render `$10` provenance

- **04F2:** IRQ graph `PRG02/03:$9F99-$A526`, 1422 bytes, preserves `$10`.
- **04F3:** fixed NMI span `PRG31:$E057-$E365`, 783 bytes, preserves `$10`; external dependencies were `$ED46`, raw bank `$0C:$89E2`, and `$E7FB`/inline dispatch.
- **04F4:** `$ED46` graph in `PRG31:$EC00-$EFFF`, 1024 bytes, preserves `$10`.
- **04F5:** raw bank `$0C` / PRG24 `$8000-$91FF`, 4608 bytes, resolved graph `$10`-clean; `$842D` left open under conservative static reachability.
- **04F6:** PRG24 `$9200-$9FFF`, 3584 bytes. Parser/bank state proves `$842D` is not live for bank `$0C`; no host-side bound is added.
- **04F7:** raw bank `$04` parser core `$8001-$87AD` is byte-identical to the audited bank `$0C` alternate-parser core. Resolved graph: 786 accepted instruction starts and no write form capable of modifying/aliasing `$10`. Metadata gives 102 bank-$04 refs / 96 roots, all alternate-parser mode.
- **04F8:** strict recursive stream work closes the first 34 bank-$04 roots through `$A013`, with the 04F7/04F8 operand-boundary repair fully reconciled.
- **04F9:** closes 32 additional bank-$04 roots through `$B1EF`; cumulative closure 66/96.
- **04FA:** closes the final 30 bank-$04 roots through semantic dependency `$BE7D`; cumulative closure **96/96**.

## 04F7/04F8 recovery repair

The restart checker found two four-byte `FE FF lo hi` commands whose operands extended beyond their original claimed spans:

```text
04F7 root $9133: $9208 FE FF 33 91 -> operands through $920B
04F8 root $9E85: $A010 FE FF 85 9E -> operands through $A013
```

`tools/audit_nmi_bank04_prg08_tail.py` now asserts complete operand containment before reading any multi-byte command parameter.

Authoritative 04F8 dependency:

```text
raw bank $04 / CPU $920A-$A013
3594 bytes
SHA-256 728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
11 prior root-probe bytes overlap
3583 genuinely new bytes
```

Strict recursive results remain zero decoded `$E7`, zero operand escapes, and zero pointer-target escapes.

## 04F9 — physical PRG09 middle roots

Authoritative span:

```text
raw bank $04 / physical PRG09
CPU $A014-$B1EF
4572 dependency bytes
SHA-256 55e35f223091a0c50beaf7ba0561445cc5c07d11ae83bfe827abcc22aa2d5a5b
32 prior root-mode probe bytes overlap
4540 genuinely new bytes
```

32 roots close under strict recursive `FB`/`FD`/`FE` decoding:

```text
abstract parser states:            5869
unique decoded command addresses:  3776
latest command:                    $B1EC
FD calls / returns:                9 / 4
FE jumps / loops:                  20 / 62
decoded E7:                        0
operand/path/pointer escapes:      0
```

## 04FA — physical PRG09 tail closure

The final 36 metadata references share 30 distinct roots across sound IDs `$5F,$68,$6A,$6C,$6D,$6E`.

The exact semantic dependency is:

```text
raw bank $04 / physical PRG09
CPU $B1F0-$BE7D
3214 dependency bytes
SHA-256 a7f0a8308ed9335b27de8eaf3df440f0d28cd6f57fb97e4123222e3116fc5f55
30 root bytes already counted as 04F7 mode probes
3184 genuinely new bytes
```

Strict recursive result:

```text
abstract parser states:            3426
unique decoded command addresses:  2595
earliest command:                  $B1F0
latest command:                    $BE7D
FD calls / returns:                20 / 20
FE jumps / loops:                  17 / 16
decoded E7:                        0
operand/path/pointer escapes:      0
```

The raw `$E7` at `$B81A` is the low pointer operand of `$B818: FE FF E7 B7 -> $B7E7`; it is not a command. The only other raw `$E7` in the physical tail is `$BFEB`, beyond all bank-$04 reachable command/operand bytes.

Therefore the entire bank-$04 metadata producer domain cannot activate `$840F/$842D`. Combined with the already-audited parser core, **all 96/96 bank-$04 roots preserve shared ZP `$10`**.

Evidence:

- `analysis/NMI_BANK04_PRG09_TAIL.md`
- `tools/audit_nmi_bank04_prg09_tail.py`

**VPP remains 21/100 after 04FA** because raw bank `$05` and fixed `$E7FB` are still open.

## Acceleration policy

`docs/ACCELERATION_POLICY.md` now records the standing rule: use NESdev, existing Castlevania III disassemblies, CDL/traces, decompilers, Ghidra, `retrodisasm`, `nesrecomp`, NSF metadata, and automated JP<->US matching aggressively for identification and prioritization, while keeping the Japanese ROM and reproducible parity evidence authoritative.

External labels/matches remain provisional until reconciled against JP bytes/control/data flow. Dynamic traces prove observed execution, not global non-reachability.

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
raw bank $0C / PRG24              -> preserves $10 on live bank-$0C paths
raw bank $04 parser $8001-$87AD   -> preserves $10 on resolved graph
raw bank $04 all 96 roots         -> closed; no live $E7; preserves $10
raw instrument bank $05           -> unresolved
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

## Unresolved / do not assume

- whether raw instrument bank `$05` can write/alias `$10` or activate `$842D`;
- whether `$E7FB` or its inline-dispatch targets can write `$10` before rendering;
- whole-ROM type-transition / selector-frame producer closure;
- higher-level meaning of `$AD` and exact visual meanings of IRQ states;
- gameplay, stage/world, background/PPU and native-runtime systems remain largely open per the VPP rubric.

## Next manageable checkpoint

**04FB — begin raw instrument bank `$05` / physical PRG10-PRG11.**

The same metadata table contains:

```text
bank-$05 references:       84
distinct roots:            72
first root:                $87AE
last root:                 $BEE8
```

All 84 references initialize alternate-parser mode under the already-proven first-byte/instrument rule, and the bank-$05 executable parser core `$8001-$87AD` is byte-identical to the audited bank-$04 core.

Initial bounded window for 04FB:

```text
CPU $87AE-$99FF
4690 contiguous bytes
```

Start by reproducing the metadata domain and core identity, then recursively close the largest root set that fits the normal byte budget with strict operand containment and pointer-target closure. Do not open fixed `$E7FB` in the same checkpoint.
