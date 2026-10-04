# Akumajou Densetsu decomp/recomp continuity playbook

This is the durable handoff for future conversations working on `Hyperbog/CVIII-Decomp`. Read this file, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md` before new work. The repository must be sufficient to resume without chat history.

## Primary objective

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable decompilation/recompilation that can execute natively on PC. Preserve original behavior first; modern QoL/mod features are later layers.

The original ROM bytes are controlling evidence. Hardware documentation, emulator behavior, NSF/M3U data, names, and hypotheses are secondary. Never modify or commit the source ROM.

## Immutable target identity

- File: `Akumajou Densetsu (Japan).nes`
- Size: `393232` (`0x60010`)
- SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- PRG: 256 KiB, CRC32 `BA6BDD6A`
- CHR: 128 KiB, CRC32 `BF15255C`
- PRG+CHR CRC32: `E349AF38`
- Mapper 24 / Konami VRC6a

Run `python tools/analyze_rom.py <rom>` before relying on a local ROM.

## Progress metric

Primary high-level metric: **Verified Parity Progress (VPP)**.

- current score: **21/100**
- rubric: `docs/PROGRESS_METRIC.md`
- machine-readable score: `analysis/PROGRESS_SCORE.csv`
- validator: `tools/progress_score.py`

VPP is evidence-based, not a labor/time estimate and not raw disassembly-byte coverage. Category weights are fixed. Increase it only when a committed artifact satisfies the rubric; corrections may reduce it. Every checkpoint report includes current VPP and whether it changed.

A future conservative ROM-byte/code-data coverage ledger must be reported separately, never substituted for VPP.

## Non-negotiable fidelity rules

1. Never guess code/data boundaries or routine semantics; uncertain material stays unresolved.
2. Every translated routine must reconcile instruction-by-instruction to authoritative ROM bytes.
3. Track **physical PRG bank + CPU address**; banked CPU addresses are not globally unique.
4. Model VRC6 bank writes and interrupt-side restoration exactly.
5. Preserve 6502 widths, flags, wrapping, zero-page aliasing, stack/interrupt behavior, and unusual cross-function control flow.
6. Never extend a table because following bytes merely decode plausibly; prove boundaries from consumers/producers/control flow.
7. Do not add host-side bounds/default behavior absent from the ROM until producer domains are proved.
8. Preserve arithmetic literally where host semantics differ. PRG26 Y/control decoding uses sign-selected carry + `ROR`, not signed division.
9. Preserve non-local returns. `PRG26:$8070` can execute `PLA; PLA; RTS` and return directly past `$8001`.
10. Preserve shared zero-page state. OAM attribute cache `$10` is not initialized at object/descriptor entry and is also unrelated gameplay scratch.
11. Keep uncertain names conservative.
12. NSF/M3U are corroborating audio evidence only; ROM bytes remain authoritative.
13. No original ROM bytes are committed to GitHub.
14. Every substantive checkpoint updates `docs/PROGRESS.md`; update this file when methodology, VPP rules, fidelity pitfalls, or the current handoff target changes.

## Manageable checkpoint policy

Each user `continue` means **one bounded checkpoint**:

1. read current continuity/progress/metric/identity and branch head;
2. choose only the listed next question;
3. regenerate the relevant ROM evidence;
4. add/update focused analysis/audit/source artifacts;
5. update `docs/PROGRESS.md` and VPP only if earned;
6. commit;
7. stop and report.

Do not combine unrelated subsystem work. If a dependency expands scope, record it for the next checkpoint.

## Cartridge model

Mapper 24 / VRC6a CPU PRG map:

- `$6000-$7FFF`: 8 KiB PRG RAM
- `$8000-$BFFF`: 16 KiB switchable PRG ROM
- `$C000-$DFFF`: 8 KiB switchable PRG ROM
- `$E000-$FFFF`: fixed final 8 KiB PRG bank

Stable fixed-bank facts:

- RESET `$E00B`
- NMI `$E057`
- IRQ `$E0F5`
- `$E2D0` tracks 16 KiB bank in ZP `$23`; `$E2D2` writes VRC6 `$8000`
- `$E2C4` selects `PRG30` at `$C000-$DFFF`
- NMI bank `$0D` call `$8001` = `PRG26:$8001`
- IRQ raw bank `$01` = `PRG02/PRG03`

## IRQ stable checkpoint

Authoritative IRQ table: `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`; `$9F5B` is code. The old `$9F60` overlap claim was false and must not be restored.

Normal states `$00-$2C`; `$80` is high-bit bypass. Highest explicit chain: `29 -> 2A -> 2B -> 2C`.

IRQ exits differ:

- `$E118`: clears VRC6 IRQ Control `$F001`, then falls through
- `$E11D`: acknowledges `$F002` and restores bank state

See `analysis/PRG02_IRQ_dispatch.md` and `analysis/IRQ_STATE_MACHINE.csv`.

## OAM/sprite stable facts

Read `analysis/PRG26_SPRITE_FORMAT.md`, `analysis/SPRITE_SET_TABLE.csv`, `analysis/SPRITE_MASTER_TABLES.csv`, `analysis/OAM_OBJECT_FIELDS.csv`, and `analysis/ZP10_OAM_STATE.md` before changing this subsystem.

- `PRG26:$8001` iterates 28 render slots in seven parallel 28-byte arrays `$0400-$04C3`.
- `$048C,X` is a byte offset into first-level block `$817F-$819C`.
- `$0400,X` is a byte offset into the selected frame-pointer window.
- 15 selectors are windows into five master pointer blocks: `$819D-$82F4`, `$8AB0-$8C2D`, `$9545-$9620`, `$9E6D-$9F6C`, `$AAA6-$AC5B`.
- `$16/$18/$1A/$1C` alias `$00/$02/$04/$06` and can select tile `+$80` under `$AD != 0`.
- descriptor byte 0 is sprite count; records are variable width:
  - Y/control bit0 clear: `Y,tile,attribute,X`
  - Y/control bit0 set: `Y,tile,X`, reusing cached final attribute ZP `$10`
- full records update `$10`; compressed records reuse it unchanged.
- `$9FA9` begins with three compressed records before its first explicit attribute.
- `$0454,X` operation is `(descriptor_attr & $FC) | full_object_byte` when nonzero; do not mask the object byte to two bits.
- `$04A8,X == 0` selects mirrored rendering; mirror toggles attr `$40` and uses `$F8-X` transform.
- OAM traversal adds `$C4` per sprite and frame seed adds `$44`.
- OAM-full path executes `PLA; PLA; RTS`, skipping the rest of `$8001`.
- descriptor census: 745 unique referenced descriptors, max 27 sprites, max encoded length 96 bytes, 2,310 compressed attribute-reuse records.

### `$9FA9` reachability chain

`$9FA9` requires selector `$10` + frame `$14`.

- 04D: PRG22 `$8745` was rejected; its owning type `$26` uses selectors `$12/$08`, not `$10`.
- 04E1: PRG18 type `$E1` was rejected; selector `$10` frames `$E8/$EC` mutate only to `$EA/$EE`.
- 04E2: direct PRG06/07 selector-`$10` setup frames are high values; direct frame `$14` is paired with selector `$0E`.
- 04E3: fixed animation supplies the transitive mutation. PRG06 `$823E-$8251` picks animation `$09` when base Y is `$A0-$A7`; selector-`$10` animation record `$09` at `$F28D` is `14 08 02`, so `$EF93` writes frame `$14`.
- 04E4: fixed object loop X range is `$01-$12`; primary type `$08` routes through bank `$09` common dispatch to bank `$03`, `PRG06:$8021`. Internal state `$01` reaches `$81E0`, writes `$0470=$40`, and can reach `$823E`. The same scheduler iteration can run movement integration and `$EF93`. Selector `$10` + frame `$14` resolves to descriptor `$9FA9`.
- 04E5: state `$00` sets base Y `$C0`, calls `$FF15` to clear movement state, then sets vertical high velocity `$0520=$FE` while `$0537=$00`. State `$01` leaves those velocity bytes unchanged; bank `$0B` movement integration therefore moves Y by exactly `-2` per scheduled tick. For the currently established state-0 consumer index domain `$00-$0E`, target-Y values at `$840F[0..14]` max out at `$98`; the trajectory must therefore pass through `$A6`, which selects animation `$09`.

Exact conditional machine path now established:

```text
slot X=$01..$12
primary type $08
-> bank-$09 common dispatcher
-> bank-$03 PRG06:$8021
-> state $00: Y=$C0, vertical velocity=-2
-> state $01: target <= $98 for established index domain $00-$0E
-> Y necessarily reaches $A6
-> selector $10 / animation $09
-> fixed $EF93 tick
-> frame $14
-> PRG26 descriptor $9FA9
```

Remaining reachability caveat: the root/creation producer domain of `$0645,X` is not yet closed. Because state `$00` and `$01` index tables using `$0633+$0645`, do **not** infer `$0645` bounds from table shape alone. Until producer values prove the index remains within `$00-$0E`, unconditional normal-gameplay `$9FA9` reachability is not claimed.

See:

- `analysis/PRG22_8745_OWNER.md`
- `analysis/PRG18_E1_SELECTOR10_FRAME.md`
- `analysis/PRG06_SELECTOR10_DIRECT_DOMAIN.md`
- `analysis/PRG06_SELECTOR10_FIXED_ANIM.md`
- `analysis/PRG06_TYPE08_823E_OWNER.md`
- `analysis/PRG06_TYPE08_VERTICAL_PATH.md`

## Native baseline

- `src/oam_renderer.hpp`
- `src/oam_renderer.cpp`
- `tests/oam_renderer_test.cpp`

The structured lift keeps NES RAM explicit and preserves wrapped 8-bit pointer indexing, variable-width descriptors, persistent `$10`, full-byte `$0454` behavior, mirror/tile transforms, clipping, OAM permutation, and the non-local OAM-full effect via an explicit result.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary handoff files:

- `docs/DECOMPILATION_CONTINUITY.md`
- `docs/PROGRESS.md`
- `docs/PROGRESS_METRIC.md`
- `docs/ROM_IDENTITY.md`

Always fetch current file/branch state immediately before editing. Never claim a GitHub change exists until commit/ref is confirmed.

Primary hardware reference: NESdev Wiki, especially VRC6, VRC IRQ, VRC6 audio, CPU, PPU, and APU. Hardware docs explain hardware; ROM bytes control game-specific behavior.

## Required behavior in future chats

When the user says `continue`, perform actual ROM analysis and commit **one bounded checkpoint** before replying. Reverify ROM identity when the ROM is available. Update VPP only if its fixed rubric earns points. Never count unresolved work as translated.

## Current next checkpoint

**04E6 — primary-type `$08` `$0645` producer domain only.** Trace root/creation writes that establish `$0645,X` before type `$08` state `$00`, and prove whether `$0633+$0645` stays within the established `$00-$0E` consumer domain. Do not expand into renderer cached-attribute `$10` ordering yet.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp in `Hyperbog/CVIII-Decomp` on branch `decompilation`. Read `docs/DECOMPILATION_CONTINUITY.md`, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md`, inspect current branch state, and treat the verified Japanese Mapper-24 ROM as immutable controlling evidence. Work one bounded checkpoint only, preserve 6502/VRC6/PPU/APU/interrupt/stack/shared-zero-page semantics exactly, do not invent bounds/table boundaries, update VPP only under its fixed rubric, and commit before reporting. Current next checkpoint: 04E6, close the root primary-type `$08` `$0645` producer domain and prove or reject the `$0633+$0645 <= $0E` bound without expanding into renderer `$10` cache ordering.
