# JP0711 — Original Japanese CHR/palette evidence acquisition

**Source:** user-supplied 393,232-byte Japanese mapper24 VRC6 iNES; SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Public source contains no original ROM, CHR bytes, gameplay traces, or copyrighted tiles.

## Why this diagnostic exists

The private JP0710 geometry handoff decoded background tile/attribute operations but could not certify a live Stage 1-01 room chain, physical CHR bank sequence, or complete palette. JP0710's private extraction package has **not been committed** to this repository; this is an independent acquisition tool, not a claim that the JP0710 source is already integrated. It also does not rebuild the original ROM or alter playable Enhanced Edition rendering.

- `JP/decomp/tools/mesen_jp_chr_palette_0711.lua` is a passive Mesen2/MesenCE observer. It logs NES PPU `$2000–$2007`, Konami VRC6 `$B003` / `$D000–$D003` / `$E000–$E003` register writes with CPU PC, mapped physical PRG offset or explicit unknown, event order, emulated frame, and CPU cycle.
- For each completed frame it logs **eight independently mapped physical 1-KiB CHR-ROM pages** using Mesen's PPU address conversion, 32 NES palette *indices*, and RAM selectors `$34/$35/$36/$07A0/$19`. Unresolved/noncontiguous CHR page slots appear as `--`, never guessed.
- `JP/decomp/tools/audit_mesen_chr_palette_0711.py` authenticates the exact owner's cartridge, Mesen ROM SHA-1 against accepted full-file/headerless forms, source limits, CHR page bounds, ordered writes/frames/cycles, 32 palette bytes, NES hardware palette aliases, and a clean script completion marker. Reset, savestate load, truncation, missing footer and incompatible data fail closed.

## Private Mesen evidence collection

1. Load the authenticated Japanese cartridge and run the Lua script **after normal boot**, before Stage 1 gameplay. Play naturally into successive rooms. Do not inject memory or load states/reset while tracing.
2. Stop the script, preserving the `JP0711_END` line, and export the Mesen script log **privately**. Do not commit the log or save state.
3. Validate it:

```sh
python3 JP/decomp/tools/audit_mesen_chr_palette_0711.py --smoke
python3 JP/decomp/tools/audit_mesen_chr_palette_0711.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --trace "/private/JP0711-Mesen.log" \
  --out "/private/JP0711-validated.json"
```

The existing private Windows Enhanced package can include these same source files under `CVIII-Enhanced/Tools/JP0711/` and a launcher writing only beneath `CVIII-Enhanced/Assets/Geometry/JP0711/`. Source scripts are not a redistributable resource pack and the output is a diagnostic report rather than a drawable world map.

## Validation and boundaries

**Locally passed:** independent ROM-free 2-frame trace smoke, seven negative/corruption cases; original Japanese SHA-256 accepted and USA edition rejected. **Not passed or claimed:** Lua execution under a live Mesen session; naturally witnessed Stage 1 identity or room adjacency; complete scanline/PPU-dot palette/CHR timings; actual RGB rendering calibration; original-vs-native pixel parity.

**VPP remains 31/100; strict semantic PRG 49,504/262,144; R-002 OPEN.** No live-game geometry or stage-source progress has been certified by this recorder alone. The next evidence step is to correlate observed room-state triples and original CHR/palette activity with the JP0710 private tile/attribute decoder, then independently prove world coordinates and native frame equality. Use symbolic IDs when importing verified room content for future editing/modding; keep physical locations in a separate provenance layer.
