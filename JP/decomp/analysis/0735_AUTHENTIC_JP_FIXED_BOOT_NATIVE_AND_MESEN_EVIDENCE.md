# JP0735 — Authenticated original Japanese fixed-bank native boot, MesenCE evidence

## Exactly what is now native

The original Japanese VRC6 cartridge, provided privately by the owner, authenticates as SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (393,232-byte iNES image; 262,144 PRG + 131,072 CHR bytes). The *source-authenticated* fixed 8 KiB program window at CPU $E000–$FFFF occupies PRG bank 31 (physical 4 KiB banks 62/63). Reset vector at iNES $4000C–$4000D is `0B E0` (CPU $E00B). The original boot code starts with the following exact four instruction sites:

| Original guest PC | iNES byte offset | Guest instruction | Opcode(s) | Native bus semantics |
| --- | --- | --- | --- | --- |
| $E00B | $3E01B | CLD | D8 | Real fetch + dummy read pc+1 with final-cycle IRQ/NMI poll; D=0 |
| $E00C | $3E01C | SEI | 78 | Real fetch + dummy read pc+1 with final-cycle poll; I=1 |
| $E017 | $3E027 | LDX #$FF | A2 FF | Real fetch + immediate read pc+1 with final-cycle poll; X=$FF and N/Z updated |
| $E019 | $3E029 | TXS | 9A | Real fetch + dummy read pc+1 with final-cycle poll; S=X |

`cviii_original_boot_native_0735.c` implements only those **five opcode bytes / four instruction entries**, using the exact CPU operations and cycle-order of pinned NESRecomp `cpu6502_interp.c`. Every other instruction continues through the unmodified upstream interpreter. The production runtime selects these small handlers by default, controlled by `JP0735_ENABLE_ORIGINAL_BOOT_NATIVE` at compile time; disabling it restores the prior interpreter-only binary. Nothing writes new guest code or changes timing functions, mapper registers, PPU, APU or DMA.

**Fail-closed guards:** The JP0733 game-owned entry authenticates the exact original retail ROM **before** starting a guest instruction. At *every* candidate instruction boundary, `cyc_native_has` verifies mapped PRG ROM (never WRAM/CPU RAM), physical 4 KiB bank **62**, exact guest PC and original opcode; at $E017 it also verifies the immediate byte $FF. Upstream dispatch additionally requires `!hw_prg_modified`. A changed program/bank therefore falls back to the interpreter rather than blindly entering compiled code. An unexpected mutation during an already-authorized opcode fetch terminates rather than silently reusing an invalid native operation.

No unverified translation of longer routines is claimed. These entry points are a constrained, source-proven *instruction-level* pilot and do not establish correctness of broader PRG control flow. The original strict semantic decompilation coverage ledger is not increased.

## Independent synthetic 6502/hardware parity proof

`JP/decomp/tools/jp0735_original_boot_fixture.py` generates a **wholly invented** Mapper24 cartridge which begins at the same CPU addresses with those standard four 6502 instructions, but fills the intervening original-game PPU status polling path with **ten invented NOPs** and a synthetic JMP loop. No original game's level, title, audio, pixels, or instruction span is copied into the fixture. The production ROM gate never accepts this test image; only a dedicated test-only compile-time bypass allows it.

Linux CI builds two entire independently linked native 6502/Mapper24/PPU/APU executables, one with `JP0735_ENABLE_ORIGINAL_BOOT_NATIVE=OFF`, the other ON, both using the same publicly generated artificial cartridge. The test **requires all four native hit counters nonzero** and compares all fields in twenty complete per-frame `--hash-out` records between interpreted and native execution. The earlier JP0732 and JP0734 synthetic full-frame regressions remain separate.

## Original MesenCE source evidence and authenticity limits

Checked *locally* using the user-provided private original ROM and archived owner MesenCE run `JP0718-20261023-213546-MESEN-RAW-INPUT.zip`:

- The source ROM reset vector and all four opcodes/one immediate are exactly as the table above.
- Original MesenCE's hardware log records CPU **$E02C**, fixed physical $3E02C (PRG-relative, no iNES header), during frame **2** at cycle **57,849**, while original room selector RAM $0035 moves from $03 to $00. This is an independent indication the original boot execution reached initialization **past** the four candidate native sites. It is **not** per-instruction trace parity for those four instructions.
- The original archived run contains **256** screenshots/snapshots and ends on route selector **00/03/00**, at frame **17,472**, with user stop at frame **17,562**.
- The existing JP0719 native replay contains **245** captured snapshots and used the verified original input schedule SHA-256 `27b502aaeca9f5d5381f9f9a812cc188043d083d8ac8b3a89bc40c70f3c30196`. Its final recorded room selector was **00/01/00**, not **00/03/00**. It was produced **before** JP0732–JP0735.
- `JP/decomp/tools/verify_jp0735_original_boot_evidence.py` reproduces the private owner-ROM and archived-capture identity/boot/mismatch checks without extracting or exporting ROM, screenshots, RAM or input logs.

**Critical nonclaim:** These old recordings do not constitute an authentic Japanese ROM vs new JP0735 executable cycle, pixel, timing or gameplay parity result. We have not executed the new JP0735 binary against the private original ROM on a live machine in this commit. The 20-frame synthetic integration proof verifies the native/interpreter boundary and correct CPU/hardware cycles **for the invented fixture**. It does not resolve the known original-vs-old-native Stage 1 gameplay divergence.

The next authenticated retail parity step is fully unattended local comparison using the original owner ROM and previously captured controls/MesenCE snapshots, recording machine cycle/frame/PPU/RAM and only enabling additional native PC/bank entries after evidence agrees. **Do not ask the user to play Stage 1 again.** No ROM, generated assets, private image, or compiled copyrighted material belongs in the public repository.

VPP remains 31/100 and strict PRG semantic coverage remains 49,504/262,144 (18.8843%); this narrowly scoped pilot is not credited as a completed game function.
