# Shared NES/FDS file-catalog and CPU trace comparison — evidence note

**2026-10-09; reusable library progress, not a gameplay or semantic checkpoint.** Grounded format references: [FDS disk blocks](https://www.nesdev.org/wiki/FDS_disk_format), [fwNES FDS image wrapper](https://www.nesdev.org/wiki/FDS_file_format), [Nintendo QD image](https://www.nesdev.org/wiki/QD), [Nintendulator nestest trace discussion](https://forums.nesdev.org/viewtopic.php?p=241032), and [P virtual status bits](https://forums.nesdev.org/viewtopic.php?t=22679).

### Implemented

1. Read-only FDS/QD side/block parser checks block 1 disk signature, block 2 declared file count, block 3 file metadata, block 4 file size and source offset. Supports FDS sides of **65,500 bytes** (with or without the standard 16-byte header) and QD sides of **65,536 bytes** (CRC words present but **not verified**). Exposes side/image and per-file content SHA-256 hashes, file names, BIOS load addresses and file-type metadata, without exposing code or assets.
2. Identifies **possible hidden file records** after the visible file-count field, with no inferred BIOS liveness or copy-protection claim.
3. Parses CPU **pre-instruction register** rows from Nintendulator/nestest text and from explicit JSONL, and compares PC/A/X/Y/P/SP in order; optional cycle comparison and optional saved PRG-bank field checks. Reports bounded differences, hashes and the first divergent instruction, not whole copyrighted log disassembly.
4. Strict evidence separation: synthetic fixtures verify parser behavior, **not** a FDS game's identity or load path and **not** a 2A03 reference trace. Real disk/BIOS media are deliberately absent.

### Local test acceptance

- FDS format/parser: **14** synthetic tests, including header/trainer geometry, multiple sides, QD CRC space, incomplete file blocks, two-file counts, hidden pair and no-payload-output conditions.
- Trace format/parser: **16** synthetic tests, including first mismatch attribution, cycle opt-in, optional mapped physical bank and status-bit conventions.
- Previous shared NES fingerprint/mapper tests: **26+9**; combined shared-library suite **65** tests.
- Run all of them via `JP/tools/run_native_regressions.sh` with no retail ROM in CI; game-specific exact JP ROM tests remain a separate, opt-in local mode.

### Unproved

No independent `nestest`/Mesen/FCEUX trace has yet been ingested, so **CPU/interrupt reference parity remains OPEN**. No supplied FDS image has been decoded; QD checksum correctness, sound/sprite emulation, FDS BIOS behavior and game code liveness remain OPEN. No new strict PRG coverage and **no new VPP point**: original JP ledger **49,404/262,144 (18.8461%)**, weighted VPP **25/100**, completed semantic checkpoint **0507**, PRG31 frontier **FB96**.
