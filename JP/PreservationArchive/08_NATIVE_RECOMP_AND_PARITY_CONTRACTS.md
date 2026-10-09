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
