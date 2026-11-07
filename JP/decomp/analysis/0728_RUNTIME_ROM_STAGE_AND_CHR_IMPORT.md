# JP0727–JP0728 — Launch-time original-ROM resources (native C11)

## Final distribution architecture and actual milestone

The intended finished Enhanced Edition workflow is:

1. User launches the installed native executable (no local compiler, Python, or asset-builder script).
2. On first launch, the original legally obtained Japanese Mapper24 cartridge is selected, SHA-256 authenticated, and remembered by an installation-level settings service (the remembered-path service is **future work**).
3. Built-in game-owned resource decoders construct the **vanilla/default** content catalog — stages, metatiles, CHR art, palettes, fonts, sprite definitions, music, hitboxes, object placements and route graph — from that exact ROM.
4. A validated local versioned cache may be written and atomically reused where useful. Cache format and persistent lifecycle are **future work**; the current implementation produces resources in private *memory*.
5. The Enhanced native game and optional mods reference stable resource IDs, while original ROM-derived gameplay behavior remains the default.

This milestone implements a concrete, **first subset**: authentic Stage 1 tile geometry (8 rooms, 1,040 32px metatiles, 16,640 8px tile IDs/palette selectors), together with the entire 8,192-tile (131,072 CHR pattern bytes / 524,288 decoded 2-bit pixels) Japanese CHR art index. The remaining domains are not yet decoded into the common game-owned resource pipeline.

## Runtime implementation

- `JP/recomp/native/enhanced/cviii_runtime_resources_0727.c/.h` implements platform-independent SHA-256 and exact original-ROM identity, with a transactional in-memory importer accepting the **runtime** path. It checks exact original SHA256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, consumes a 393,232-byte iNES image privately, and frees the raw image after constructing the typed resources. It does not rely on Python or external SHA libraries.
- `cviii_game_resources_open_0727(path, &atlas, &chr)` constructs both the original Stage 1 atlas and all CHR tile art in **one file read and one SHA256** check. Existing JP0598 original font/CHR consumers can reuse the exact `CviiiChrIndex` buffer layout and source-identity checks. If a vetted CHR index has already been provided, the caller passes `NULL` and keeps it.
- `cviii_stage1_host_0725.c` delegates to that loader and no longer depends on `CVIII_STAGE1_ROM_PATH` or the earlier FNV-only per-renderer identity guard. It preserves the strict original CPU/PPU game state, all 61,440 native-center pixels, and the JP0726 actual-nametable room and camera validation.
- `cviii_edition.c` passes the game-owned original CHR index registry to the renderer, allowing automatic generation when the asset-index sidecar is missing. It also retains the explicitly supplied `--asset-index` behavior for older private builds.
- `JP/recomp/release/alpha/Launch-Alpha.ps1` already offers a first-launch ROM file picker and independently authenticates the ROM. It now automatically passes that selected full path to the binary through `--stage1-world-rom` in Enhanced Edition, rather than forcing a renderer compile-time path. A wrong/missing ROM fails closed to the stock picture.

**No** raw ROM bytes, game-derived art, generated asset packs, or retail binaries are committed to the public repository.

## Compile-time caveat — not yet a standalone distributable recomp

The native NESRecomp game-logic compilation itself still requires `JP_ORIGINAL_JP_ROM` during `nesrecomp_add_cycle_game(... ROM ...)` and the private Alpha builder still compiles game-specific C and generates historical cached asset sidecars. **JP0727 does not remove that build-time game-logic dependency.** It removes the Stage 1 atlas's compile-time file-path dependency and makes *these two resource classes* native, ROM-sourced and automatically generated at launch.

The finished no-compiler user installer requires a separate, substantial game-logic compiler/distribution transition, persistent ROM-path management, cache schema/version negotiation, mod load-order contracts, and remaining original game-data decoders. Avoid advertising the current private alpha as that final product.

## Tests and safety boundaries

- FIPS-180-4 SHA-256 standard vectors: empty, `abc`, 56-byte boundary and 64-byte block.
- Independent production test: completely invented synthetic mapper24 image is rejected, even when the file length and iNES mapper match; the caller's previous atlas/CHR are unchanged.
- Separate, explicitly flagged `CVIII_RESOURCE_TEST_SYNTHETIC_0727` test build: wholly artificial source is accepted; atlas resolves expected tile IDs and attributes, and the runtime CHR index matches the original JP0598 tile-to-pixel decoding schema.
- Malformed synthetic Stage 1 source fails transactionally: previous atlas and graphics index are not destroyed.
- Windows 2022/MSVC checks compile the real game-owned compositor in the windowed synthetic NESRecomp test, plus two independent retail-rejection and synthetic-acceptance resource test executables.
- Original-ROM CHR bytes and independently computed 2-bit decoded pixel FNV signatures match the preserved JP0598 source digests. This authenticates the format independently of the newly written importer, not a new original-game gameplay parity observation.

Neither source-level tests nor Windows synthetic CI certify that all offscreen live graphics have correct mid-frame CHR banks, animated level tiles or raster palettes. No extra VPP or historical strict semantic PRG bytes are awarded. **VPP 31/100; strict PRG 49,504/262,144 = 18.8843%.**
