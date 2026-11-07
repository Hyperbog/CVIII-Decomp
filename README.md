# Castlevania III — Decompilation and Native Recompilation

Original-game source recovery, deterministic validation, and native NESRecomp development for *Akumajou Densetsu* (Japan), with separate North American research.

**Canonical Japanese target:** Famicom Ricoh 2A03 CPU with Konami VRC6 mapper 24. The North American cartridge has different mapper hardware and must not substitute for Japanese ROM evidence.

## Project structure

| Location | Responsibility |
| --- | --- |
| [JP/decomp/](JP/decomp/) | 6502 disassembly, semantic recovery, authenticated research, preservation records and tests |
| [JP/recomp/](JP/recomp/) | Native C11/SDL2 NESRecomp integration, optional Enhanced presentation, build and release tooling |
| [NA/](NA/) | North American research, kept distinct from the Japanese target |
| [SharedDecomp/](SharedDecomp/) | Shared source methodology and validation contracts |
| [.github/workflows/](.github/workflows/) | Automated verification and platform-specific build gates |

**Start here:** [JP overview](JP/README.md), [native Windows build/release guide](JP/recomp/release/alpha/README_ALPHA.md), [decompilation overview](JP/decomp/README.md).

**Policies:** [AGENTS.md](AGENTS.md), [mod-forward methodology](MOD_FORWARD_METHODOLOGY.md), [contribution guide](CONTRIBUTING.md), and [2026-11-07 consolidation record](docs/BRANCH_CONSOLIDATION_2026-11-07.md).

## Active branch and validation

`decompilation` is the repository's default branch and sole long-lived integration branch. Historical feature and research files are retained, but a file's presence does not mean it is linked into the active native runtime, that parity has been proven, or that its tests have passed. The original game's behavior remains the baseline and Enhanced modifications are opt-in.

Never commit copyrighted ROM/NSF material, generated proprietary game code/assets, private recordings or save states. Authentication, mapper-24 source identity, 6502/PPU/APU accuracy and independent emulator evidence are required where claimed.
