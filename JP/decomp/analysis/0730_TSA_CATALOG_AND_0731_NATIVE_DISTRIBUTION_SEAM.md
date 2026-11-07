# JP0730–JP0731 — Cross-stage TSA source catalog and the native-logic distribution boundary

## Broader original Japanese ROM pattern decoding (JP0730)

The Japanese ROM-specific map at https://gmvania.blogspot.com/2012/08/bookmark-this-blog-entry-last-update.html gives candidate physical file spans for background **TSA (tile assembly) definitions**, distinct from room-layout references. Each complete TSA pattern is a 4×4 grid of 8×8 background tile IDs, 16 bytes total.

`cviii_rom_tsa_catalog_0730.c/.h` decodes and retains **1,478 structurally bounded patterns = 23,648 tile IDs** from fourteen original source regions:

| Region | Original iNES file span inclusive | 16-byte definitions |
| --- | --- | ---: |
| Catacombs | $0182D0–$0187CF | 80 |
| Abandoned Mines | $018EDB–$019EDA | 256 |
| Main Hall | $01A2FB–$01A8FA | 96 |
| Inner Hall | $01AC9A–$01B269 | 93 |
| Castle Keep | $01B592–$01BD51 | 124 |
| Causeway | $01C459–$01C9B8 | 86 |
| Swamp | $01CD94–$01D143 | 59 |
| Alucard's Cave | $01D78E–$01DD8D | 96 |
| Sunken City | $01E3BE–$01E9BD | 96 |
| Lookout Tower | $01EDFA–$01F3C9 | 93 |
| Wallachia | $020451–$020D60 | 145 |
| Forest | $022120–$02263F | 82 |
| Ghost Ship | $022C7D–$0232BC | 100 |
| Tower | $023737–$023BB6 | 72 |

**Clocktower is deliberately excluded.** The published physical span $02141A–$021965 contains 1,356 bytes = 84×16 + 12 bytes, which does **not** fit the required 16-byte tile-definition alignment. Do not silently round to 84 and invent an unverified ending. A future original CPU pointer/resource-consumer trace must settle the actual boundary.

The 14 accepted source spans and counts were checked against the owner's SHA-256-authenticated original Japanese ROM. The layout decoder rejects unknown image sizes/mapper IDs; the high-level resource loader remains responsible for cryptographic source authentication.

**Important distinction:** This is the pattern-definition layer only. For thirteen non-Wallachia regions we have NOT yet authenticated the attribute-byte provenance, room-selector maps, room orientation, stage routes, or live PPU-consumer semantics. Therefore the catalog deliberately returns `has_attributes=0` outside verified Wallachia, and it does not claim those stages are renderable as complete preloaded worlds. Wallachia (Stage 1) has its independently validated 145-byte palette attribute table. Synthetic-only C11/MSVC tests cover all 14 bounded spans, the 1,478 entries, and blocked Clocktower.

## Why the gameplay executable still needs ROM-at-build (JP0731)

This is a **separate engineering dependency** from stage/CHR extraction.

The actual pinned `mstan/nesrecomp` commit `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1` implements `nesrecomp_add_cycle_game(target ROM ...)` in `runner/cyc/project.cmake`. ROM is a **required** configure argument (line 54). That CMake function builds the host NESRecomp generator, calls `tools/cyc/prepare_project.py --rom ... --recompiler ...` at configure time, then includes the generated `sources.cmake` file listing ROM-specific `game_cyc*.c` sources. The Python bridge invokes NESRecomp with the ROM to generate those C translation units. Current CVIII's `JP/recomp/native/nesrecomp_cycle/CMakeLists.txt` follows this exact path and validates `JP_ORIGINAL_JP_ROM` at configure time.

It would be wrong to say that supplying `--stage1-world-rom` at launch removes the build-time ROM dependency: it supplies only asset data to the Enhanced renderer, not original 6502 instruction semantics needed by the ROM-specialized translated game code.

### Necessary final separation

1. Maintain **developer-only** ROM-specific static recompilation as a source-verification and native-optimization tool while the original semantic decomp is incomplete.
2. Make end-user runtime gameplay load from the **authenticated ROM**, with a portable general CPU/mapper/PPU fallback for bytes without verified independent native handlers. Authenticated native semantic handlers must be selected only when they correspond to proven original instructions/entry points; do not dispatch stale static generated code from a different cartridge.
3. Convert those native handlers into an independently linkable game engine/ROM-identity-specific translation layer, or another genuine runtime translator. This must be evaluated for copyright/distribution implications and for exact mapper-24 timing and original gameplay parity.
4. Only then can a **prebuilt** executable be distributed which accepts the legally obtained ROM on first launch without requiring end-user compilers. CMake `ROM` remains needed for ROM-specialized developer code generation until that rearchitecture is implemented.
5. Add cache/asset schema upgrades and mod overrides independent of the original CPU semantics, preserving an Original reference mode.

No change in this PR purports to resolve step 2 or to distribute compiled original game instruction code. The newly created TSA catalog is independent ROM-derived source data and currently a dormant reusable module in the game target, not evidence of Stage 2–15 geometry parity. No commercial ROM, CHR artwork, game code, private cache file or native commercial executable was committed.

**VPP = 31/100, strict semantic PRG = 49,504/262,144 bytes (18.8843%)**, unchanged.
