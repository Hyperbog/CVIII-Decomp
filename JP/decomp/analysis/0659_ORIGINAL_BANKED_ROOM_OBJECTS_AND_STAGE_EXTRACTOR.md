# JP0659 — Bank-qualified Japanese room-resource installer and reversible stage data

**Subsystem:** original Japanese Castlevania III stage/room loader; physical
16KiB Konami VRC6 raw PRG0A ($8000–$BFFF), temporary raw PRG0E
($8000–$BFFF), shared fixed PRG31 ($E000–$FFFF).
Owner-original iNES length 393,232, SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Physical PRG0A SHA `1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`;
physical PRG0E SHA `9fc30168f3eca751de893aac2af31b5f4c40b8dcdcde1ad70b9614c607c29bb5`.

## 1. Connected original 6502 → compiled native state transition

This is the **complete 124-byte original** source routine at
**raw0A:$B7F7–$B872**, SHA-256
`068cd9f225e38a3b2f0b6e19717bfa11b73a68b9419854d684c42cf55d66d15d`,
not an invented room record parser. Its source root selector is the original
`$07A0`, with *conditionally valid* values **0–4**. The original
five 16-bit source addresses are encoded at raw0A:$B8C2–$B8CB.

It calls fixed PRG31:$FB96–$FBA4 (15 authentic original bytes,
`A9 0E / JSR $E2D0 / LDA ($08),Y / PHA / A9 0A / JSR $E2D0 /
PLA / RTS`). Fixed $E2D0–$E2D5 writes original RAM $23
and mapper port $8000. **Every source byte read is mapped
from physical PRG0E, then the original bank 0A is restored**
before the caller resumes. This is not an original-US Mapper5 path.

The tested source instruction sequence:

- `$B7F7–$B806`: fetch pointer from $B8C2 + 2*$07A0, save it
  as $08/$09; Y=0.
- `$B808–$B82C`: read the first resource byte **twice**
  (Y=0), extracting high and low nibbles to $34 and $35;
  read second byte twice (Y=1), extracting high nibble to
  $36, low nibble to $54 and low bit to $72. Clear $53.
  This repeated-read detail is critical for actual mapper
  switch count and original execution time.
- `$B831–$B83F`: consume header bytes Y=2/Y=3 into
  $07A1/$054E. Begin records with Y=4 and X=1.
- `$B842–$B86F`: read **five raw bytes per record**
  via five individual $FB96 crossbank calls, and write them
  respectively to `$048C+X`, `$0400+X`, `$0438+X`,
  `$041C+X`, `$04A8+X`; write $054E+X=$01.
  The first byte $FF is a terminator and **is not installed**
  as a record. $FF in later fields is valid data.
- `$B872`: original RTS, with source Y=4+5*record_count,
  X=1+record_count, A=$FF, C=1/Z=1/N=0,
  and V preserved from entry. Mapper bank returns to 0A.

The record byte values remain **uninterpreted raw source fields**,
not invented object IDs, artwork or enemy attributes.

### All five source streams — physically complete, no gaps

The **175-byte original physical PRG0E source interval**
$BE8B–$BF39 is contiguous and SHA-256 authenticated:
`977745b341cfa56056be96e454d2e49e5d91084b798e82b1a1e819dcfcdab479`.
It contains **five four-byte headers, 30 five-byte record instances,
and five $FF terminators**: 20 + 150 + 5 = **175 source bytes**.
Do not count these records as 30 distinct executed original gameplay events.

| Selector $07A0 | PRG0E CPU root | Record count | Source reads/case | Mapper writes/case |
| ---: | ---: | ---: | ---: | ---: |
| 0 | $BEA4 | 10 | 57 | 114 |
| 1 | $BEDB | 7 | 42 | 84 |
| 2 | $BF03 | 4 | 27 | 54 |
| 3 | $BE8B | 4 | 27 | 54 |
| 4 | $BF1C | 5 | 32 | 64 |
| **Total per five-selector sweep** | | **30** | **185** | **370** |

Original physical source **execution/record representation**:
124 original raw0A instruction+operand bytes and 175 typed raw0E
data bytes = **299 physically bank-qualified bytes** in the
bounded newly resolved consumer/data unit. This is source-semantic
evidence, **not 299 newly certified strict PRG bytes**; both
banks were previously represented in raw-content/structural atlases.

## 2. Native C11 implementation with real original 6502 oracle

- `JP/recomp/native/enhanced/cviii_room_stream_0659.h/.c`:
  read-only output containing full original non-stack RAM postcondition,
  A/X/Y/C/Z/N/V, root, record count, all mapper byte-write
  events, read count, and final bank. Error/unknown-domain returns
  leave caller data unmodified. Original selector values **5–255**
  are **not** asserted safe by the game; the native importer
  deliberately rejects them pending full $07A0 producer bounds.
  Source bank inputs are authenticated by the replay wrapper
  before this helper runs. It is dormant; no runtime mapper write.
- `JP/decomp/tools/jp_room_stream_0659.py` fetches actual original
  opcode/operand bytes and models JSR/RTS + real 6502 stack,
  all $FB96 and $E2D0 opcodes, a bank-qualified physical
  raw0E `LDA ($08),Y`, original $8000 mapper transactions,
  branches, and RAM/register/flag updates. The actual JP-ROM SHA,
  raw0A/raw0E SHA, 124-byte code span and the original 175-byte
  stream span are pinned. Unsupported bus or instructions fail.
- **1,280/1,280 original-ROM 6502 ↔ compiled C11 cases PASS**:
  five actual source roots × **all 256 seeded RAM variants**.
  They executed **879,360 physical original 6502 instructions**,
  compared **2,293,760 nonstack RAM bytes**, tracked
  **47,360 source reads** and **94,720 precisely ordered**
  mapper register byte writes with no divergence.
  Every source root, 30 cumulative decoded record instances
  and final original A/X/Y/C/Z/N/V matched.
  All initial bank contexts explicitly use $23=$0A.
- `JP/recomp/native/enhanced/cviii_room_stream_test_0659.c`:
  **1,280 entirely invented-source cases** on all five stream
  roots, all 256 RAM seeds, five-field installs, variable
  original record lengths, valid $FF non-command fields,
  and exact bank/event ordering; rejects corrupted pointers,
  missing FF, bad input lengths, wrong mapper and invalid selector,
  preserving output on every rejection.
  Both GCC and Clang strict C11, Clang ASan+UBSan passed locally.

No external emulator was used to capture a **naturally reached**
$B7F7 game-frame source event. This is independently original
*opcode fetched* reference versus native postcondition parity,
**not independent Mesen gameplay liveness or 6502 cycle parity**.

## Stage-selector correction — Part 17

The five JP0659 streams are **not evidence for Stage 1 spawn definitions**.
The original raw0A loader writes the high nibble of each first header byte
to RAM `$34`; the other header outputs are `$35`, `$36`,
`$54`, `$72`, `$07A1`, and `$054E`. The authenticated original
raw0E headers, in `$07A0` selector order 0–4, produce RAM `$34`
values **`$04, $01, $08, $02, $0B`** respectively.
**None** produces RAM `$34=$00`. Calling the 30 decoded records
Level 1 candle/enemy spawns was incorrect.

The private JP0659 exporter now emits derived `header_ram_effects`
with the exact original 6502 destination registers, plus a
`ram_0034_zero_stream_count` summary. The packer rejects contradictory
metadata (without breaking earlier version-one exports that lack it).
The synthetic smoke includes negative checks for both metadata
classifications. This is a classification/safety fix, **not** a wider
camera, gameplay activation implementation, new source-PRG certificate,
or proof that every `$34=0` object comes from a particular bank.

For a verified Stage 1 actor path, see
[`0509_MESEN_ACTOR_LIVE_FINDINGS.md`](0509_MESEN_ACTOR_LIVE_FINDINGS.md):
original raw0A `$84F3 → $8501 → $8B2C` creates two type-`$3D`
actors under the recorded Stage 1-02 state. That witness is not a
complete list of Level 1 enemy/candle placements or offscreen schedules.

## 3. Actual reversible stage resource tooling

`JP/decomp/tools/jp_room_resources_0659.py` provides a **fully
reversible, editor-oriented room resource schema**:
`JP-VRC6-original-room-resource-fivebyte/v1`. With
`--rom` and `--export`, it creates a **private local JSON**
containing five stable stream IDs, 30 stable per-record IDs,
ROM and physical-bank provenance, correct original CPU source
addresses, four raw header bytes and five independently editable
byte fields per record, mapped destination RAM offsets and
exact FF termination. Only user-owned original ROM bytes are
exported; no game content is embedded in the tool, repository
CI or docs.

Using `--input` and `--pack`, it validates and serializes
the five resources back to a **175-byte private resource block**,
not to a whole licensed ROM and not into a live mod API.
Original-JP ROM extraction → JSON → serialization reproduces
**175/175 original source bytes and the exact original SHA-256**.
ROM-free synthetic full-bank JSON roundtrip and **seven independent
malformed-source/schema rejection classes** also PASS.

Reproduce locally:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG \
  JP/recomp/native/enhanced/cviii_room_stream_0659.c \
  JP/recomp/native/enhanced/cviii_room_stream_test_0659.c -o /tmp/jp0659-test
/tmp/jp0659-test
python3 JP/decomp/tools/jp_room_stream_0659.py --smoke
python3 JP/decomp/tools/jp_room_resources_0659.py --smoke
cc -std=c11 -O2 -shared -fPIC \
  JP/recomp/native/enhanced/cviii_room_stream_0659.c -o /tmp/libjp0659.so
python3 JP/decomp/tools/jp_room_stream_0659.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --native-lib /tmp/libjp0659.so --seeds 256
python3 JP/decomp/tools/jp_room_resources_0659.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --roundtrip --export /tmp/jp0659-room-editor-private.json
python3 JP/decomp/tools/jp_room_resources_0659.py \
  --input /tmp/jp0659-room-editor-private.json \
  --pack /tmp/jp0659-local-source-block.bin
```

## 4. Fixed rubric certification

This forms two **distinct reusable** stage architecture results:

1. **Stage/room data formats: second of five points**:
   Original JP physical raw0E five-byte room-object record format
   and actual raw0A bank-switched loader state effects, complete
   executable native decode of all 175 physically contiguous
   source bytes and five pointers, 1,280 actual original-6502/native
   event and RAM comparisons. This is distinct from the first
   data-format point (JP0657's bank0A *three-level 4/7-byte
   pointer hierarchy*).
2. **Reproducible stage-data extraction tooling: first of two
   points**: source-ROM SHA-authenticated JSON extraction,
   stable per-stream/per-record IDs and raw byte positional field
   provenance, a validated editor-schema packer, exact original
   175-byte private roundtrip, and explicit malformed-input
   rejection. Second tooling point still OPEN for broader
   stage world resources and actual authoring/export integration.

**VPP: 29 → 31/100, Stage/world 1 → 3/20.**
No scrolling/transition, collision-map or stage progression
subpoints are earned. Full original-$07A0 producer-domain bounds,
the $B6A4 carry gate, entry through natural RESET→NMI gameplay,
actual object behavior, CPU-cycle/PPU parity and native playable
game remain OPEN (R-001/R-002).

**STRICT PRG BYTES DO NOT CHANGE:** 49,504/262,144 (18.8843%).
Previous checkpoint 0508 and fixed physical PRG31 frontier
$FB96 remain intact. The 299 newly reconstructed **conditional
source bytes** are not added to the strict cumulative certificate
without an independent original reference-emulator natural trace
and historical overlap reconciliation. The source and tests
deliberately avoid inventing that trace.
