# JP0731 — ROM-independent native content-library build gate

The new `JP/recomp/native/content_runtime/CMakeLists.txt` builds the original-Japanese content importer as a **standalone C11 static library** and a small metadata-only CLI probe. CMake does **not** accept or inspect a ROM path, and does not fetch or depend on the external NESRecomp compiler, SDL2, Python, or generated `game_cyc*.c`.

`cviii_content_probe_0731 original-jp.nes [private-cache-path]` validates the exact legally owned Japanese Mapper24 ROM **when the executable is run**. It loads the predecoded Stage 1 atlas (eight rooms / 16,640 tile positions) and all 8,192 source CHR tiles. The probe prints only counts and resource-schema metadata, not proprietary ROM data. The source image is released after loading; an optional private cache uses the versioned JP0729 canonical format. The probe does **not** execute any game instructions and is NOT a replacement for the actual gameplay recompilation.

Separate native tests cover (1) production-loader rejection of wholly invented ROM contents, (2) explicitly synthetic-test-only acceptance plus cache creation/reuse/repair, and (3) all structurally decoded cross-stage TSA definition regions. Linux and Windows MSVC build and run these tests without any copyrighted ROM. The `CVIII_RESOURCE_TEST_SYNTHETIC_0727` bypass is compiled **only** into the isolated synthetic test target, not the production `cviii_original_rom_content_0731` library or CLI.

### Distribution boundary

**Achieved:** resource extraction, private cache and CHR generation can be shipped as built native code that uses the original Japanese ROM only at launch.

**Not achieved:** the NESRecomp gameplay binary still configures from the original ROM, invokes the compiler to generate ROM-dependent C translation units, and requires its separate mapper-24 runtime. Nothing in this content-only target certifies original gameplay parity, replaces the 6502 program, or legalizes redistribution of ROM-derived native code. The next phase must isolate CPU/mapper emulation and authenticated native gameplay handlers from this build-time generator before a true ROM-independent game executable is possible.

No new VPP or original semantic byte-ledger credit. No ZIP, ROM, extracted graphics, private cache or compiled retail code was committed.
