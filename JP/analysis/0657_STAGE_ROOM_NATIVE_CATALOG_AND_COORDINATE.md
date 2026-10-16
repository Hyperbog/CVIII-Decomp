# JP0657 — Stage/room hierarchy native decoder and original-6502 room-coordinate parity

**Authoritative image:** Original Japanese Akumajou Densetsu (Japan) Mapper24 VRC6 ROM,
393,232 bytes, SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Source physical raw **16KiB PRG bank 0A**, SHA-256
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`,
conditionally mapped to CPU `$8000–$BFFF`. No US game mapper or source was substituted.
No proprietary ROM bytes or complete stage/graphics payload are committed.

## A. Native complete typed room-source catalog

`cviii_room_catalog_0657.c/.h` is a reusable read-only C11 source-data
consumer for the original `$801E–$8046` selector hierarchy.
The **original 41-byte CPU lookup** is authenticated with SHA-256
`31d3ba22edd5ef269b08f4c4322bbe78bd34588d186a500a9c1edee4de0c13f8`.
It reads `$34/$35/$36`, traverses source `$92AE`,
stores intermediate `$06/$07` and `$04/$05`, and produces
`$95/$96`. This is an original-code path, not a fabricated
modern room-pointer formula. It was previously source-classified
in JP0538 and individually compared in JP0539; JP0657 adds **a native
complete 16KiB input validator and usable typed leaf registry**, not a
second byte-count claim for the earlier pointer algorithm.

The original physical source population is fully bounded:

| Room-data component | Original source extent | Structural count |
| --- | --- | ---: |
| First tier `stage` pointers | $92AE–$92CB | 15 words |
| Second tier pointers | $92CC–$931F and $9AF4–$9B1F | 64 words |
| Third tier pointers | $9320–$93CB and $9B20–$9B81 | 135 words |
| Distinct four-byte roots | $93CC–$9AF3; $9B82–$9F6D | 113 roots |
| All four-byte cells | same two contiguous source pools | **709 cells / 2,836 bytes** |
| Distinct seven-byte roots | $AB1F–$AFA3 | 16 roots |
| All seven-byte records | $AB1F–$AFA3 excluding 16 terminals | **163 records / 1,141 bytes** |
| Seven-byte terminator bytes | last byte of each 7-byte source stream | 16 `$FF` |
| Source-indexed selectors | across 15 stage groups and 64 nested tables | **135 choices / 129 unique roots** |

Total **4,421 bytes** in the hierarchy and two typed record pools:
428 pointer bytes plus 2,836 four-byte-cell bytes plus
1,157 seven-byte source-pool bytes. These source bytes were
**already structurally cataloged in JP0538**; no new strict-PRG
certification is asserted.

The C11 catalog accepts a supplied 16KiB physical source, verifies
all 15+64+135 pointer groups, sorted first/second tiers, physical
bank bounds, the 113 unique 4-byte roots, complete stride/coverage of
709 cells, and all 16 7-byte stream boundaries, terminal `$FF`,
first-field value domain `$00–$03`, 163 records and no escaped
pointer. It reports typed source intervals per indexed selector and
does not export copyright-bearing payloads. Failed validation leaves
the prior output unchanged. Public mod identifiers are **not**
CPU offsets; this is a private historical provenance resolver only.

`JP/tools/jp_room_catalog_0657.py` independently replays
the **actual original source 6502 instructions**
at `$801E–$8046` for each of 135 valid selector triples,
then compares each original final leaf with the compiled native
C11 `cviii_room_catalog_find_0657` response and the full
source-root interval. **135/135 original-ROM/native matches PASS**.
A fully artificial **15/64/135** bank fixture, entirely ROM-free,
tests all 135 retrievals and corrupted pointers, terminators,
record tag and malformed input. It uses no original game data
records. GCC/Clang C11 and Clang ASan/UBSan passed locally.

## B. Original 6502 coordinate/room-state computation

`cviii_room_coordinate_0657.c/.h` lifts the connected
original physical bank0A routines:

- **$8001–$801D**: 29-byte helper, SHA-256
  `a5bfb0b51b7d7e50ec5dbc1fd882490136b49e0d91f9245aa06dea86aa19a6bb`;
  uses CLC, ADC, PHA/PLA and two exact 6502 `ASL A; ROL $73`
  pairs for a 16-bit room-coordinate transform.
- **$80D1–$8107**: 55-byte caller and phase setup,
  SHA-256 `73e0e407e4a2151a9af018b41f000e7ab4fd4d6693fccd594cef6cc29b7ac014`.
  It executes JSR $8001, distinguishes $62 zero/nonzero,
  masks and conditionally sign-extends low six bits of $53,
  writes $08/$09/$0E, adds the $08 adjustment into $73,
  writes $0A=1, and exits after LDY $73 at **$8108**.

The helper is read-only, models all final A/X/Y and
**carry/zero/negative/overflow** states, and produces
five specific scalar RAM postconditions. The reference program
fetches/executes the actual original 6502 opcodes, including
stack push/pop for JSR/PHA/PLA, branch decisions, and byte/carry
arithmetic. **131,072/131,072 original-ROM/native C11 matches PASS**
for every 256×256 initial coordinate and both $62 branch classes.
Maximum original reference instruction count is **41 per case**.
Independent ROM-free C11 covers the same 131,072 cases using
bitwise shift/rotate semantics, and Python covers 1,024
8-bit wrap and carry cases. GCC/Clang and sanitizers passed.

**Boundary:** This checkpoint stops before the original
`LDX $8410,Y` consumer and does not assert that its Y
domain is bounded during natural game execution.
Neither the stage-record parameter meanings, complete
room loader/scrolling flow, original Mesen natural entry
or original-vs-native PPU frame parity are established.
The two native modules are **dormant**; no player-facing
gameplay, PPU, UI or audio behavior changes.

## Reproduce against the private original JP cartridge

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG \
  JP/native/enhanced/cviii_room_coordinate_0657.c \
  JP/native/enhanced/cviii_room_coordinate_test_0657.c -o /tmp/jp0657-coordinate
/tmp/jp0657-coordinate
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG \
  JP/native/enhanced/cviii_room_catalog_0657.c \
  JP/native/enhanced/cviii_room_catalog_test_0657.c -o /tmp/jp0657-catalog
/tmp/jp0657-catalog
python3 JP/tools/jp_room_coordinate_0657.py --smoke
python3 JP/tools/jp_room_catalog_0657.py --smoke
cc -std=c11 -O2 -shared -fPIC JP/native/enhanced/cviii_room_coordinate_0657.c -o /tmp/jp0657-coord.so
cc -std=c11 -O2 -shared -fPIC JP/native/enhanced/cviii_room_catalog_0657.c -o /tmp/jp0657-catalog.so
python3 JP/tools/jp_room_coordinate_0657.py --rom "$JP_ORIGINAL_ROM" --native-lib /tmp/jp0657-coord.so
python3 JP/tools/jp_room_catalog_0657.py --rom "$JP_ORIGINAL_ROM" --native-lib /tmp/jp0657-catalog.so
```

## Certification and remaining work

The checked-out complete typed **stage/room source format**,
now with a validated native C11 import/resolver and an
original-instruction 6502 replay, satisfies **one** of the
five fixed `Stage / world / progression: stage/room data formats`
subpoints (formal decision separate). **VPP 28 → 29 / 100**;
stage/world 0 → 1 / 20. The other four data-format
subpoints, every scrolling/transition, collision map,
route/progression, menu/end-flow and stage-data extractor point
remain OPEN until independently proved. No claim of full world
reconstruction or live game-frame parity.

**Strict game PRG:** unchanged **49,504/262,144 (18.8843%)**.
The original 84 coordinate source bytes and full catalog
were already source-accounted in JP0538/0539; no new independent
original-Mesen gameplay live-coverage witness.
VPP, strict PRG and playable game percentage are distinct.
Fixed PRG31 frontier **$FB96**, last semantic checkpoint **0508**,
R-002 **OPEN**.
