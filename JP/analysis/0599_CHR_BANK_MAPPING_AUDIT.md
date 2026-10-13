# JP0599 — Read-only VRC6 CHR bank mapping and sampled palette audit

Status: **C11 mapper-mode diagnostic complete; authentic-JP frame-end
CSV pending a private owner Windows play session**. No gameplay or
rendering substitution has been enabled.

## Physical mapping and bounded observations

JP ROM: original Japan 393,232-byte mapper24 VRC6a, 131,072-byte
CHR-ROM => 128 pages of 1 KiB / 8,192 tiles.
Pinned external runtime commit:
2b4fcdb98c9e702be3fb365cfc645003c50b5fc1.

The pinned \`runner/cyc/hw_vrc6.inc\` function \`vrc6_apply()\` writes
eight live mappings via \`map_chr1(page, bank)\`. In
\`runner/cyc/hw_mapper.c\` the result is
\`(bank & (chr_pages - 1)) * 1024\`, with 128 pages for retail JP.

With \`mode = ctrl & 3\` and pages 0..7:
- Mode 0: register \`r=page\`; eight independent banks.
- Mode 1: register \`r=page/2\`; paired 1 KiB windows.
- Modes 2/3: pages 0..3 use registers 0..3 and pages 4..7
  use \`r=4+(page-4)/2\` in pairs.
- If the mode pairs a page and control bit 5 is set, the low bit
  of its CHR bank becomes \`page & 1\`.
- Take \`bank & 127\` and verify the observed \`cart.chr_off[page]\`
  equals \`bank * 1024\`; reject missing/duplicate/misaligned fields.

The game-owned module uses NESRecomp's **public** read-only
\`cyc_hw_state_dump(FILE*)\` and \`cyc_ppu_palette()\` interfaces.
No internal \`HwCart\` layout, host-side memory poke, or emulator
mapper source patch is needed.

The Windows Alpha's \`-ChrAudit\` launch switch (Enhanced only)
adds \`--chr-audit CVIII-CHR-Audit.csv\`. Each 60th completed frame,
the host dumps mapper state to a temporary stream, recomputes all
eight physical CHR pages, and logs the eight bank IDs, active PPU
palette (32 bytes), and mapper parity PASS/FAIL. The cache is the
existing authenticated read-only original-JP CHR index.

### Tests, interpretation, and gates

ROM-free C11 test cases cover modes 0..3, bit-5 paired-page override,
physical CHR bank wrapping, corrupted bank offsets, and invalid
snapshot field alignment. The isolated edition host contract links
against two mock read-only diagnostic functions; synthetic mapping
and real windowed SDL2 builds remain distinct CI gates.

**A frame-end register snapshot is not a scanline/PPU-dot trace.**
It cannot establish in-frame CHR bank timing, background/sprite fetch
routing, nametable source, palettes during the frame, or full pixel
parity. Original still renders directly from the stock PPU frame,
and Enhanced still uses the same image unless the earlier explicitly
experimental unlimited-sprite compositor is enabled.

Next: capture multiple Japanese game rooms and companion/route
scenarios with the audit enabled, compare mapping observations with
the original PPU renderer, and add per-scanline/fetch evidence only
where necessary. Don't enable cache-backed drawing prematurely.

Strict semantic PRG 49,504/262,144 and VPP 27/100 unchanged.
