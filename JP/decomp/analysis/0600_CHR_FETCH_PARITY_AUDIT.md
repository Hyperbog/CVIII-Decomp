# JP 0600 — Actual PPU physical CHR fetch parity (sampled)

## Scope / intent

Extend JP0599's **end-of-frame** mapper-bank/palette snapshots with
read-only observation of the **pattern bytes the original NESRecomp
PPU actually fetches** during selected whole frames. These audits are
diagnostics for JP0598's owner-private CHR cache, not a substitute
graphics renderer and not a new semantic 6502 translation.

Pinned runtime: \`mstan/nesrecomp\` commit
\`2b4fcdb98c9e702be3fb365cfc645003c50b5fc1\`.
Japanese cartridge: mapper 24, 131,072 CHR bytes, 128 physical
1 KiB pages, 8,192 16-byte 2bpp tiles.

## Hook and non-mutation invariant

The pinned \`hw_ppu.c\` pattern read path invokes
\`hw_cart_chr_read(addr)\` when its actual PPU read pin is enabled.
The generated owner-private \`hw_mapper.c\` overlay adds a
\`cviii_chr_fetch_set_hook\` callback, enabled by the Enhanced host
for **one in every 60 frames**. The CHR ROM read is performed exactly
as before, from \`hw_cart.chr[hw_cart_chr_index(addr)]\`.
Only after obtaining that byte does it send the PPU pattern address,
original physical CHR offset, actual returned byte, scanline and
dot to the observer. It never substitutes data, writes mapper or
PPU state, alters clocking, or controls the original game.

The observer checks two independent cache representations:
- The original \`chr/raw_2bpp.bin\` physical ROM byte.
- The 8 NES pixel indices in the corresponding plane/row from
  \`chr/pixels_u8.bin\`, re-encoded to that same exact byte.

For each observed PPU page it records the first/last physical 1 KiB
bank used and the number of transitions between banks within a
scanline. This catches transient bank selection not visible at a
frame-end snapshot. The two presentations remain separate:
\`cyc_frame_argb\` (reference PPU) and the optional existing
experimental sprite compositor; **no cache-backed drawing** yet.

## Local reporting and validation

Launch the private Windows Alpha with
\`Launch-Alpha.ps1 -Edition Enhanced -ChrAudit -Rom <JP-ROM>\`.
The launcher emits \`CVIII-CHR-Audit.csv\` and
\`CVIII-CHR-Fetch.csv\` beside the game executable.
The independent \`JP/recomp/tools/jp_chr_fetch_report_0600.py\` tool checks
the exact per-PPU-slot CSV schema, frame sample cadence, sorted
scanlines, physical CHR page bounds, impossible/missing transitions
and mismatch counters; its \`--require-parity\` option exits
nonzero when a pattern read contradicts the local cache.
It needs only the private CSV, not original ROM bytes.

ROM-free CI:
1. Verify the source overlay anchors and reject a duplicate patch.
2. Test a synthetic CHR bank-switch timeline containing both matches
   and a deliberately mismatched fetch, with no game ROM.
3. Compile the *actual* native C11 SDL2 game host on Windows and Linux
   with an invented mapper24 cartridge, preserving frame and
   save-state hash regressions.
4. Check the CSV parser against synthetic valid/malformed samples,
   including page 127, invalid page 128, repeat samples and
   impossible transitions.

## Evidence remaining

The observer compares **fetched pattern data at actual read times**,
not full rendered graphics. Sprite selection, background nametable
source (including VRC6 ROM nametables), scanline palette updates,
priority, scroll and composition still require separate evidence
before using the cached graphics as the Enhanced renderer.

Authentic Japanese gameplay data must be captured locally for
different stages, companions and boss encounters. Synthetic
CI pass is not proof of authentic stage or complete pixel parity.
No copyrighted private ROM, CHR archive, or actual game trace is
committed or uploaded by public CI.

Strict PRG semantic coverage remains 49,504/262,144;
VPP 27/100, JP0508 and fixed PRG31 $FB96 frontier unchanged.
