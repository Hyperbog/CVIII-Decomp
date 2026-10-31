# JP — Whole-room native resource and diagnostic rendering integration

**Implementation:** native room geometry/CHR association, metatile definitions and palette attributes, and an optional side-by-side rendering callback for the existing C11 NESRecomp Enhanced runtime.

**Canonical ROM:** Japanese *Akumajou Densetsu*, VRC6 mapper 24, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. The U.S. MMC5 version is rejected. No ROM contents, generated cartridge assets, savestates, or gameplay recordings are included in the repository.

## Implementation boundaries

- `cviii_whole_room.h/.c`: `CVROOM1` read-only, authenticated-source geometry pack. 135 room selectors, 130 deduplicated 16x16-metatile grids. Records have source offsets, orientation, dimensions, and ROM-selected CHR R2/R3/R5/R6 values.
- `cviii_room_gfx.h/.c`: `CVGFX01` metatile resources, 15 source groups and 1,563 32x32 definitions, each with sixteen 8x8 pattern IDs and one four-quadrant palette attribute byte. The selected group is based on the ROM's stage/area/room dispatch including exceptional switches.
- `cviii_room_renderer.h/.c`: native color buffer rendering with explicit CHR 1 KiB mapping and 16 background palette colors supplied by the host. Supports arbitrary room camera origins and native image dimensions; no write to emulated hardware state.
- `cviii_room_preview.h/.c`: opt-in 512x240 diagnostic composite; original 256x240 frame copied byte-exactly on the left, reconstructed background view on the right. Fails closed to original presentation if resources or selectors are unavailable.
- `cviii_edition.c` and `native/nesrecomp_cycle/CMakeLists.txt`: integrate the four C modules into the already working host; selectors read from Japanese runtime RAM `$0034/$0035/$0036`. Original simulation, PPU, mapper, IRQ, OAM, audio and save-state machinery are unchanged.

The preview uses initial R4=`0x40`, room-selected R5/R6 and initial R7=`0x43`, and reads the host's current 16-color background palette. **It does not claim frame/scanline-accurate VRC6 mapper/IRQ/CHR or palette reconstruction**, full offscreen actor simulation, or parity with Stage 1 gameplay. Camera inference from `$0057/$0056` is not yet validated for every room.

## Owner-local data preparation

Generate these **outside Git**, using your legally owned authenticated Japanese ROM:

```sh
python3 JP/recomp/tools/build_room_resources.py --rom "/private/Akumajou Densetsu (Japan).nes" --out "/private/CVIII-Rooms.dat"
python3 JP/recomp/tools/build_room_graphics.py --rom "/private/Akumajou Densetsu (Japan).nes" --rooms "/private/CVIII-Rooms.dat" --out "/private/CVIII-Graphics.dat"
```

The existing private Windows build also generates `CVIII-CHR-Index.dat` from the same original ROM. Launch the enhanced game using:

```
--asset-index /private/CVIII-CHR-Index.dat --room-resources /private/CVIII-Rooms.dat --room-graphics /private/CVIII-Graphics.dat --room-preview 1
```

Those owner-local cache files are 655,368 + 21,168 + 28,075 = 704,611 bytes, sufficient for eager native preload. Do not redistribute the caches. Invalid cache content and unknown selectors are rejected by the resource interfaces. The diagnostic view is off by default.

## Validation performed before commit

- Original ROM authenticated; generated private room and graphics caches byte-identical to the previous recorded SHA-256 digests `da80c441803e786ea4767a6bfc758432af4a7c617ca49a52bf824bc89807bf99` and `37e07c03cd9eabbe667a02ab1692829de67e9d49dc31c7aa9402bbb0626dccf6`.
- Standalone C11 modules and tests: 135/135 rooms, 15/15 groups, 1,563 definitions, 1,080 independent pixel checks, corrupt-pack rejection and 512x240 presentation preservation PASS.
- Prior checkpoint: exact comparison callback compiled against synthetic host and sanitizer tests passed. **This is not a complete NESRecomp/SDL build or live Stage 1 gameplay**.
- A prior offline Stage 1 room render was 768x192 but used synthetic grayscale colors. Its proprietary image is not committed.

## Final-release resource loading contract (not yet implemented)

On first installation, authenticate a user-provided Japanese ROM and atomically build versioned private caches keyed to ROM SHA and schema version. On game startup, validate/preload a global room directory, metatile tables and CHR graphics (less than 1 MiB). On room changes, use the original running game to select immutable resources, not a duplicate gameplay state machine. Later add independently verified typed collision/hazard, spawn, transition, palette-event and sound-resource sections as needed. Do not infer those systems from this background-only cache. Make future mod-facing IDs stable and symbolic; retain ROM addresses only as provenance.

## Evidence and scope

The permanent `JP/recomp/reference/NES_Recomp_Master_Reference.csv` is unchanged: its existing `PRG`, `LEVELS`, `CHR`, `METATILES` and `VRC6` domain rows already describe these ROM facts. Runtime/synthetic/host test data belong in standalone engineering tests, **not** the ROM-only master. The full native Windows/SDL build and authenticated live gameplay acceptance remain open.