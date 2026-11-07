# Contributing

## One-branch workflow

Use the default `decompilation` branch for continued integration. Do not create additional long-lived feature branches. Keep the existing four workstream locations (`JP/decomp`, `JP/recomp`, `NA` and `SharedDecomp`) stable unless a complete source-path and build migration has been validated.

## Before claiming a change is complete

1. Read [AGENTS.md](AGENTS.md) and [MOD_FORWARD_METHODOLOGY.md](MOD_FORWARD_METHODOLOGY.md).
2. Keep code, relevant documentation and regression checks together.
3. For ownership changes run `python3 JP/decomp/tools/audit_workstreams.py`; for related regressions use `bash JP/decomp/tools/run_native_regressions.sh`. Run platform builds and relevant end-to-end acceptance separately.
4. Require genuine, authenticated owner-ROM/reference-emulator evidence before declaring 6502, mapper, audio, PPU or native gameplay parity; synthetic tests are not equivalent.
5. Never check in copyrighted game ROMs, NSF files, derived retail assets, proprietary generated game code, save states or credentials.

The [historical branch consolidation record](docs/BRANCH_CONSOLIDATION_2026-11-07.md) identifies recovered sources and deferred glue integration. Many restored files remain research or dormant modules until individually wired and verified.
