# NES / FDS / Konami Preservation Research Source Catalog

Research snapshot: **2026-10-09**. Sources below are discovery/reference resources, **not licenses to redistribute commercial ROMs, developer software or BIOS files**. Community material is technically valuable but falls below original ROM execution and verified hardware traces. Specific editions, errors, dates and licenses should be rechecked when each resource is used. **Do not infer a universal Konami engine from publisher identity.**

## Supplied local primary and secondary documents

| Resource | Scope and material examined | Evidence status / limitations |
|---|---|---|
| `mcs6500_family_programming_manual.pdf` | MOS Technology, *MCS6500 Microcomputer Family Programming Manual*, second edition, January 1976, **265 PDF pages**, official MOS-era instruction/programming reference | Primary-source **NMOS 6502 family**, **not** NES 2A03 board, PPU, decimal-disable or VRC6 specification. Consult NES-specific corrections before behavioral claims. |
| `NESDoc.pdf` | Patrick Diskin, *Nintendo Entertainment System Documentation*, v1.0, August 2004, **47 PDF pages**; preface credits Jacobs, Covell, Firebug, Chadwick, Loopy, Fayzullin, early Nesdev | Historical synthesizer of emulation-community knowledge, not Nintendo's original development documentation. Verify aging details against modern NESdev. |
| `EveryNES.pdf` | no$cash *Everynes Hardware Specifications*, **109 PDF pages**; inspected CPU/PPU mapping, Famicom vs NES connector differences, VRC mapper and the FDS reference sections | Valuable reverse-engineering compendium. **Not automatically a hardware test result.** Its NTSC/PAL clock phrasing and other old claims need checking against modern specialized tests. |
| Supplied retail JP/US `.nes` files | Original-byte control, mapper and regional comparison; **not** authorization to publish bytes | Ground truth for **their respective versions**; cross-title comparisons remain hypotheses until traced. |
| Supplied JP `.nsf` and `.m3u` | Sound extraction context | Cannot substitute for original game sound event schedule; track IDs must be ROM-correlated. |

## Hardware and cartridge reference tier

| Resource | Link | Use / caveat |
|---|---|---|
| NESdev hardware reference guide | https://www.nesdev.org/wiki/NES_reference_guide | Current index of CPU, APU, PPU, FDS, file formats and test suites; starting point for correction history |
| 2A03 / CPU | https://www.nesdev.org/wiki/2A03 | NES CPU/APU/IO properties; 2A03 arithmetic does not implement 6502 decimal ALU mode |
| NES iNES format | https://www.nesdev.org/wiki/INES | Header/trainer handling; **legacy headers can contain garbage and mapper ambiguity** |
| NES 2.0 | https://www.nesdev.org/wiki/NES_2.0 | Mapper/submapper and exponent/linear ROM sizes; do not misread size high nibble |
| Konami VRC6 mapper | https://www.nesdev.org/wiki/VRC6 | Mapper 24/26 address A0/A1 swap, bank windows, IRQ/audio registers |
| VRC6 audio | https://www.nesdev.org/wiki/VRC6_audio | Hardware channel register model; does not reveal any game's song/voice data format |
| FDS hardware | https://www.nesdev.org/wiki/Family_Computer_Disk_System | RAM adapter, disk system, IRQ, expansion audio and differences from cartridge games |
| FDS BIOS | https://www.nesdev.org/wiki/FDS_BIOS | Fixed BIOS entry and inline-pointer calling convention; game file/data requirements |
| PPU transistor simulation | https://www.nesdev.org/wiki/Visual_2C02 | Reference to transistor-level model; helpful when approximated sprite-0 bit signals yield bogus traces |
| Emulator validation ROM index | https://www.nesdev.org/wiki/Emulator_tests | blargg, kevtris, PPU-vblank/sprite-zero/IRQ, APU and mapper tests; independent validation priority |

## Tooling, historical artifacts, emulator internals

| Resource | Link | Reuse/verification guard |
|---|---|---|
| NESdev older archive | https://www.nesdev.org/archive.html | Historic early-2000s utilities, tutorials, VRC-VI/VII emulator, sound tools; pages explicitly warn documents may be outdated |
| 1998-era dcc6502 | https://github.com/tcarmelveilleux/dcc6502 | Historical ANSI C disassembler with register annotations and cycle counts; separate MIT license; original author reports 1998 origins |
| cc65 da65 guide | https://cc65.github.io/doc/da65.html | Code/data ranges, labels, attributed disassembly and assembler round trips; annotation configs can be distributed without ROM dumps |
| cc65 compiler/assembler | https://github.com/cc65/cc65 | Cross-development, assembler/linker, decomp rebuild fixture; licenses apply |
| Mesen2 debugger/trace/CDL | https://github.com/SourMesen/Mesen2 | Detailed NES CPU/PPU/mapper implementation and independent trace/CDL infrastructure; repo archived June 2026 and GPL-3.0; avoid direct code copying into ports |
| FCEUX debugger | https://github.com/TASEmulators/fceux | Independent code/data logger, memory tools, Lua tracing; review tool version and licenses |
| Emulator test ROM suite collection | https://github.com/christopherpow/nes-test-roms | Re-run established CPU/PPU/APU test programs with expected outputs; test ROM ownership/license must be checked individually |
| FDS free BIOS alternative | https://github.com/jamesathey/FreeDiskSysROM | Compatible independent FDS BIOS reimplementation, GNU LGPL-3.0. Its clean-room rules exclude consulting original BIOS disassembly |
| Original FDS BIOS revision configs | https://github.com/TakuikaNinja/FDS-disksys | Reproducible `da65` configs for three BIOS revisions; **BIOS images not included**; revision CRC32s documented |
| FDS vs cartridge comparative disassembly | https://gitlab.com/segaloco/fc_dk | ROM-free source/asset-extraction workflow spanning Donkey Kong Famicom cartridge and Disk System editions; independent code annotations may be inaccurate |
| NES development kit history | https://www.retroreversing.com/famicom-nes-development-kit | Secondary device/development-kit context, **not proof of available Konami source code or rights** |
| Sound-driver pattern identification discussion | https://forums.nesdev.org/viewtopic.php?p=309450 | 2026 community discussion of identifying multiple vendors' audio-driver signatures; anecdotal; supports *investigating* signature libraries, not asserted cross-game match |
| Early-era sound pipeline discussion | https://forums.nesdev.org/viewtopic.php?t=231 | Historical claims of differing publisher APU practices; treat as unverified forum recollection |

## Targeted Konami genealogy lead (additional research)

The [VGMPF community sound-driver inventory](https://vgmpf.com/Wiki/index.php?title=Famicom%2FNES_Sound_Driver_List#Konami) groups Castlevania III, Contra and Gradius II in a putative **Hidenori Maezawa** family; Metal Gear, Castlevania II and Madara in a putative **Atsushi Fujio** family; and Esper Dream 2 among unique/unknown variants. The page explicitly warns of customized branches and variants, and calls Akumajou Densetsu a possible VRC6 version. This is an **S0 community classification**, not authenticated staff attribution, exact game-engine identity, or permission to transplant code. See [working comparison queue](KONAMI_DRIVER_HYPOTHESES.md). For game-specific sound syntax, prioritize ROM-confirmed pointer/command grammar and sound-register events.

## Highest-value research queues

1. **CPU quality gate:** feed published `nestest` logs, `cpu_interrupts_v2`, `instr_test-v5`, `cpu_dummy_reads`, `cpu_dummy_writes` and unofficial-opcode fixtures into a bounded 2A03 comparison harness. Our currently modeled 151 **official** opcodes are insufficient to assume all cartridge execution paths, as confirmed by the prior hypothetical state-04 fork encountering unsupported bytes.
2. **PPU quality gate:** use `ppu_vbl_nmi`, `ppu_sprite_hit`, `ppu_read_buffer`, `oam_stress`, DMA/IRQ tests. Build sprite-0 behavior from real CHR/OAM/nametable pixels instead of forcing PPUSTATUS bit 6.
3. **Konami mapper family:** first compare VRC6a (JP Castlevania III) against VRC6b (Madara and Esper Dream 2) with bank/register canonicalization; only when a legal local ROM is available. The regional US Castlevania III is **MMC5**, not the same mapper/driver ABI.
4. **Cross-game software candidates:** look for exact stable code spans in known verified entry/callee domains, score distinctive/unique signature windows, then validate opcode start/end, 6502 8-bit flags, branches, table extents, RAM usage and mapper context. Maintain a source provenance trail and **do not promote matches merely from publisher/year or source labeling**.
5. **FDS:** model BIOS `JSR` inline word parameters and file directory/side format, then use version-specific configs with legally provided BIOS. This is shared across FDS games but is not a Konami-specific cartridge-ROM routine.
6. **Historical archive:** prioritize original developer interviews, source/utility releases, surviving manuals and research communities, while distinguishing ownership, provenance, documented author claims and plausible but unverified recollections.

### Preservation record format for newly found sources

Record `{URL, retrieval_date, title, creator, publication_year, revision/hash, rights, direct_source_or_secondary, hardware_or_game_claim, repro_steps, correction_links, JP_ROM_countercheck_status, anchor_sha256}`. This keeps useful old forums and Wayback/Internet Archive links reproducible without copying or silently endorsing them. No particular historical Nintendo/Konami first-party dev kit or original source has been authenticated by this snapshot.
