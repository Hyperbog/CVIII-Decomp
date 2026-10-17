# JP 0597 — Owner-only ROM asset index/package foundation

## Scope and evidence

Original Japanese iNES mapper24 cartridge SHA-256:
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28.
File 393,232 bytes = 16-byte iNES header + 262,144-byte
PRG ROM + 131,072-byte CHR ROM. The standard original ROM remains
unchanged. The extracted archive is **not** licensed for public
redistribution. Neither original commercial asset bytes nor a private
game binary are committed to GitHub or emitted by public CI.

JP/recomp/tools/jp_asset_pack_0597.py is a stdlib-only build/verify/read
module reusing authenticated JP/password tables from
JP/decomp/tools/jp_password_stage_0593.py. The resulting local file is
CVIII-Assets.bin (ZIP container with fixed member timestamps and
deterministic member ordering), schema cviii.jp.assets/v1.

### Indexed assets, exact physical identity

| Archive entry | Meaning | Status |
|---|---|---|
| chr/raw_2bpp.bin | All 128 physical 1-KiB CHR pages, 64 16-byte tiles per page | Complete, lossless bytes |
| chr/pixels_u8.bin | 8,192 8x8 tiles, pixel values 0..3, uncolored and unmapped | Complete, losslessly re-encodable |
| tables/password/scrambles.bin | 27 bytes, physical PRG03 offset 0x078DD | JP ROM verified |
| tables/password/name_seeds.bin | 8 bytes, PRG03 0x07911 | JP ROM verified |
| tables/password/selectors.bin | 9 bytes, PRG03 0x07B62 | JP ROM verified |
| tables/password/leaders.bin | 3 bytes, PRG03 0x07A0A | JP ROM verified |
| tables/password/valid_partners.bin | 6 bytes, PRG03 0x07AE1 | JP ROM verified |
| tables/password/save_points.bin | 45 bytes, PRG00 0x00EF1 | JP ROM verified |

Physical PRG address does not imply a fixed CPU mapped address: VRC6
bank registers still determine the visibility of CPU PRG windows.
Likewise raw CHR tiles do not identify live background versus sprite
uses. The original mapper24 translation, PPU palette RAM, pattern
bank switching and in-frame timing remain authoritative.

The manifest includes source SHA, mapper, physical PRG and CHR geometry,
SHA256 for every entry, per-CHR-page SHA256 and explicit unresolved
data families. Package load validates all members, no duplicates, no
unknown files, original-JP declared fingerprint, exact tile decode
reconstruction, per-page digest and table offsets. This verification
checks internal cache integrity; on its own it does not prove
provenance from the actual cartridge. The --build path DOES fully
authenticate the original user-owned cartridge.

### CLI

    python JP/recomp/tools/jp_asset_pack_0597.py --smoke
    python JP/recomp/tools/jp_asset_pack_0597.py --build --rom "path/to/original_JP.nes" --out "/private/CVIII-Assets.bin"
    python JP/recomp/tools/jp_asset_pack_0597.py --verify --out "/private/CVIII-Assets.bin"
    python JP/recomp/tools/jp_asset_pack_0597.py --build --rebuild --rom "path/to/original_JP.nes" --out "/private/CVIII-Assets.bin"

Building refuses an output path inside the source checkout to prevent
committing copyrighted media. The builder caches only if its full
verify pass succeeds, with atomic file replacement when rebuilding.
Windows Build-Alpha.ps1 creates/reuses the package under the private
AlphaCandidate directory, includes a schema/hash and cache-not-loaded
field in ALPHA_BUILD.json, and includes copyrighted output only in the
private ZIP. Public Windows CI runs invented 2bpp tiles and invented
password data, deterministic repeat builds, corruption rejection,
bad-ROM refusal, and separately compiles the native SDL2 target.

### Local verified original-ROM run

With the owner-supplied original-Japanese ROM, the extraction yielded
128 physical CHR pages, 8,192 tiles and eight authenticated asset
members. Rebuild of the same target path reused identical bytes.
Local SHA256 of generated package:
13ee5a40d36bcf6a085646e4cd157dd4d27032ab370d0413bff0d601ceada4c3.

**Not yet implemented:** Runtime consumption or ROM-free launching,
gameplay/stage data extraction, scene/text cutscene extraction,
music sequence handling, palette interpretation, animation
compositions, mapper-frame presentation parity, or original-vs-enhanced
pixel comparison from the new pack. These are distinct future gates.

No certified strict PRG coverage change: 49,504 / 262,144;
VPP 27/100, semantic checkpoint 0508 / fixed PRG31 $FB96 unchanged.
