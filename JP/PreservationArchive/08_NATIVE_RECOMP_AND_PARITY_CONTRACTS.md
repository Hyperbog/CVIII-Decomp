# 08 — Native Recompilation, Mapped CPU Bus and Explicit Parity Scope

**Status:** COMPONENTS IMPLEMENTED AND TESTED; native bootable game/frame parity NOT CERTIFIED. Evidence: [mapper](../analysis/NATIVE_VRC6_MAPPER.md), [IRQ](../analysis/NATIVE_VRC6_IRQ.md), [scheduler](../analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md), [VPP](../docs/PROGRESS_METRIC.md).

## Preserve observable machine behavior

Porting aim: reproduce JP game state and transitions before QoL or mod features. Original ROM and physical bank mappings control behavior. The native runtime must preserve:

- CPU-visible 8-bit A/X/Y/SP/P, 16-bit PC, little-endian addresses, carry/overflow/negative/zero and stack side effects, including unusual tail-call and double-PLA paths.
- CPU RAM aliases/mirrors, PRG RAM, VRC6 window state, mapper-register writes at their actual order, fixed program bank, and bus reads that may map to different bytes at the same CPU address.
- NMI/IRQ scheduling and PPU/OAM $4014 DMA timing, PPU $2000/$2005/$2006 latch behavior, CHR mirroring, APU+VRC6 sound devices, and object/state producer order.
- Deterministic game-observable state with host facilities separated behind explicit adapters.

The NES 2A03 is NMOS 6502-like **without active decimal arithmetic**. General MOS manual semantics inform CPU modeling, but JP ROM and observed 2A03 behavior control game effects.

## Existing native components and **exact test scopes**

| Component | Implemented scope | Existing tests | Not established |
|---|---|---|---|
| [VRC6 mapper](../src/vrc6_mapper.hpp) | PRG/CHR windows, WRAM and CIRAM | [mapper regression](../tests/vrc6_mapper_test.cpp) | entire game's register-write schedule |
| [VRC6 IRQ](../src/vrc6_irq.hpp) | mapper-side latch/control/counter/341-dot prescaler | [IRQ regression](../tests/vrc6_irq_test.cpp) | CPU interrupt latency/frame trace |
| [OAM renderer](../src/oam_renderer.hpp) | descriptor traversal and sprite-state lift | [OAM test](../tests/oam_renderer_test.cpp) | end-to-end 256-byte OAM video trace |
| [Collision math](../src/collision_math.hpp) | unsigned 8-bit distance primitive | [65,536-pair test](../tests/collision_math_test.cpp) | full gameplay collision decisions |
| [AI script address lift](../src/ai_script_dispatch.hpp) | prechecked script-record/action pointer arithmetic | [256-value test](../tests/ai_script_dispatch_test.cpp) | all BD11 prechecks, live script domain |
| [Fixed tile probe](../src/fixed_tile_probe.hpp) | mapped $FD62,Y and 12-entry tile arithmetic | [524,288-case test](../tests/fixed_tile_probe_test.cpp) | entire tile-collision routine |
| [Temporary PRG read](../src/temporary_prg_bank_read.hpp) | raw 0E read and 0A restore, bus write order | [65,537-case test](../tests/temporary_prg_bank_read_test.cpp) | 6502 stack/cycles or loader liveness |
| [Room E7FB address lift](../src/room_state_dispatch.hpp) | pointer selection and Y/C/Z/N effects | [65,536-pair test](../tests/room_state_dispatch_test.cpp) | full tail-dispatch stack/handler behavior |

## Testing ladder

1. **ROM identity/byte manifest:** exact SHA and consumed operands.
2. **Isolated algorithm:** exhaustive finite-domain input tests when tractable.
3. **CPU instruction/register trace:** compare original emulator vs native/translated execution under same RAM, bank, PPU/APU flags and interrupt schedule.
4. **Subsystem transition traces:** object states, AI scripts, collision and map loads.
5. **Frame goldens:** RAM/OAM/PPU registers/pixel frames, all routes, audio-register and PCM traces.
6. **Full playable parity:** startup to endings, save/load, UI, NPC/enemy/boss/room/route behavior. Optional fixes/QoL only after explicit separation.

A native algorithm passing tests is **not** an emulator trace match. A decomp byte can be verified without native parity. The present VPP 24/100 does not claim a bootable complete executable. Archive modifications cannot raise VPP without the rubric's durable evidence.


## 0508 general 2A03 mapped trace research harness (not an integrated native runtime)

[Reusable Python CPU/mapper harness and correction](../analysis/0508_TRACE_CORE_AND_E7FB_CORRECTION.md): 151 official 6502 opcodes, binary NES 2A03 arithmetic, 2 KiB RAM mirror, PRG RAM, 16 KiB bank switching, fixed PRG31, limited PPU/APU register-event capture, real stack/flags. Regression: **272** synthetic-state ROM path tests / **334,912** instructions through PPU clear and natural sound return; **2,048** original E7FB dispatch edge cases and **40,960** 2A03 arithmetic cases; **65,536** corrected C++ address-lift cases. No external emulator trace, DMA/IRQ/PPU timing, audio synthesis, playable native CPU core, new VPP, or strict byte credit. This is tooling toward the reference-trace gate, not its completion.


## 0508 experimental scheduler component — not integrated native parity

[Conditional JP ROM CPU-cycle/NMI scheduler evidence](../analysis/0508_EXPERIMENTAL_VBLANK_CYCLE_TRACE.md) provides a reusable Python mapped 6502 timing-class and PPU vblank-edge research harness (151 official opcode classes, 27 selected timing unit checks, 960 modeled PPU frames and 8,864,752 executed JP ROM instructions). It is not the native executable/runtime, CPU/PPU/IRQ bus-cycle integration, a reference trace comparison, or a frame/video/audio golden. R-006 remains OPEN, native VPP category remains 1/10, overall VPP 24/100.


## Reproducible native CI integration (validation milestone)

`JP/tools/run_native_regressions.sh` compiles all eight native C++20 suites with strict warning/error flags. GitHub Actions workflow `jp-native-regressions.yml` runs four ROM-free suites plus progress-rubric/archive checks; [run 37993214808](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/37993214808) passed. An exact SHA-256-checked JP ROM supplied locally enables four additional ROM-bound suites and two extra ROM-specific mapper/IRQ checks. This earns only the **CI/reproducible test gate** in validation, taking overall VPP to **25/100**. It does not prove the native platform boots, improve strict code coverage or substitute for original emulator reference-trace parity.


## Shared hardware and cross-ROM knowledge library (not native-port parity)

[Reusable NES/FDS tooling and technical policy](../SharedNES/README.md) separates universal 2A03/PPU/APU requirements, cartridge mapper families, FDS BIOS service ABI and game-specific engine routines. The source [catalog](../SharedNES/SOURCE_CATALOG.md) includes community test-ROM collections, cc65 annotation tooling, Mesen/FCEUX debug/traces and the supplied hardware manuals. `JP/tests/test_nes_reuse.py` adds 26 ROM-optional cases to the existing GitHub native regression gate, with an optional original JP↔US fixture only when the user provides those ROMs. Such metadata matching is **not** an integrated CPU/PPU native executable, no score point is added.

## Independent generic NES CPU trace milestone (2026-10-09)

[External Nintendulator nestest reference](../SharedNES/NESTEST_REFERENCE_0508.md) now verifies **8,991 sequential PC/A/X/Y/P/SP/cycle states** under NROM with a separately enabled stable-unofficial 2A03 opcode extension. [CI evidence](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38010527144) is green and both external test assets are SHA-pinned. This closes **one** of the validation trace-tooling rubric's two points, moving total VPP to **26/100**. It does **not** close the original-game CPU/interrupt parity criterion, real VRC6 bank/IRQ timing, PPU/OAM pixel verification, full playable runtime, or the verified PRG byte floor (49,404). Completed machine semantic checkpoint stays 0507.


## Real independent Japanese-ROM frame/code-data witness (not native parity)

The [Mesen original-game reference](../SharedNES/0508_MESEN_ORIGINAL_GAMEPLAY_REFERENCE.md) provides actual independently emulated Mapper-24 game execution through Stage 1 (1,100 contiguous frames) and Mesen CDLv2 physical-code/data accounting (**12,885 observed code/operand bytes**). The original game's name-entry START step was absent from the earlier synthetic input policies. This is **genuine full-system execution evidence**, not yet a stepwise side-by-side comparison with the native port or the partial Python runtime. The separate NROM/Nintendulator 8,991-state CPU test remains the only earned reference-trace tooling point. The second validation reference point, complete original-JP mapper/IRQ/frame comparison, remains OPEN. **VPP 26/100; strict PRG 49,404; no promotion by observed byte count alone.**


## Original-Mesen source-mapped reference development — checkpoint 0508

Private SHA-pinned independent Mesen2 hardware emulation executes 9,500 frame jobs including original Stage 1-02 gameplay; only the first 1,100 frames form a contiguous common trajectory, seven 1,200-frame forks deliberately diverge thereafter. [Source/reference corpus](../SharedNES/0508_STAGE1_MULTIBRANCH_REFERENCE.md). The actual fixed CPU code at $FBA5/$FBB0/$FF06/$FF14 has independently decoded instruction boundaries, physical PRG31 CODE bits and genuine breakpoints, permitting narrow **100-byte strict ROM admission** after 0507's explicit physical-gap nonoverlap check. [Machine proof](../analysis/0508_MESEN_FIXED_LIVE_PROOF.json). The native executable's video, audio and CPU/mapper *frame-by-frame* equivalence is still NOT established. **Strict PRG 49,504; VPP 26/100.**


## 0509 provisional native CPU and bus integration

The JP/native0509 C++20 headless executable compiles an official 151-opcode CPU interpreter plus the existing VRC6 mapper/IRQ classes, `$4016/$4017` controller serial I/O, partial PPU `$2000-$2007` memory and OAM bus, and modeled NMI. 262,144 exhaustive binary ADC/SBC cases and synthetic cartridge CPU/PPU/NMI integration pass. An independent original-ROM Mesen2 v2.1.1 reference matches the first 7,828 native **CPU PCs** before vblank phase divergence at instruction 7,829. That does NOT certify source-code reconstruction, CPU register/cycle equivalence, image/audio parity, or a playable native game: the executable still reads the original JP ROM. [Detailed limitations](../docs/0509_NATIVE_CPU_HEADLESS.md). **VPP 26/100, strict 49,504 bytes.**


**0509 original source execution boundary correction:** The reference-fixture PPU phase from independently recorded Mesen2 reset state is optionally set to dot 31 for original-ROM comparison; this reproduces **24,773** prefix CPU PCs before a modeled NMI entry mismatch at instruction 24,774. It must NEVER be counted as verified PPU timing, full original/native state, or playable standalone game implementation. Default vblank phase remains zero and the unseeded test still matches only the first 7,828 PCs. VPP 26; strict PRG 49,504.
