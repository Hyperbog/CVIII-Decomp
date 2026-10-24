# JP0735 — Authenticated original Japanese fixed-bank native boot, MesenCE evidence

## Exactly what is now native

The original Japanese VRC6 cartridge, provided privately by the owner, authenticates as SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (393,232-byte iNES image; 262,144 PRG + 131,072 CHR bytes). The *source-authenticated* fixed 8 KiB program window at CPU $E000–$FFFF occupies PRG bank 31 (physical 4 KiB banks 62/63). Reset vector at iNES $4000C–$4000D is `0B E0` (CPU $E00B). The original boot code starts with the following exact four instruction sites:

| Original guest PC | iNES byte offset | Guest instruction | Opcode(s) | Native bus semantics |
| --- | --- | --- | --- | --- |
| $E00B | $3E01B | CLD | D8 | Real fetch + dummy read pc+1 with final-cycle IRQ/NMI poll; D=0 |
| $E00C | $3E01C | SEI | 78 | Real fetch + dummy read pc+1 with final-cycle poll; I=1 |
| $E017 | $3E027 | LDX #$FF | A2 FF | Real fetch + immediate read pc+1 with final-cycle poll; X=$FF and N/Z updated |
| $E019 | $3E029 | TXS | 9A | Real fetch + dummy read pc+1 with final-cycle poll; S=X |

`cviii_original_boot_native_0735.c` implements only those **five opcode bytes / four instruction entries**, using the exact CPU operations and cycle-order of pinned NESRecomp `cpu6502_interp.c`. Every other instruction continues through the unmodified upstream interpreter. The production runtime selects these small handlers by default, controlled by `JP0735_ENABLE_ORIGINAL_BOOT_NATIVE` at compile time; disabling it restores the prior interpreter-only binary. Nothing writes new guest code or changes timing functions, mapper registers, PPU, APU or DMA.

**Fail-closed guards:** The JP0733 game-owned entry authenticates the exact original retail ROM **before** starting a guest instruction. At *every* candidate instruction boundary, `cyc_native_has` verifies mapped PRG ROM (never WRAM/CPU RAM), physical 4 KiB bank **62**, exact guest PC and original opcode; at $E017 it also verifies the immediate byte $FF. Upstream dispatch additionally requires `!hw_prg_modified`. A changed program/bank therefore falls back to the interpreter rather than blindly entering compiled code. An unexpected mutation during an already-authorized opcode fetch terminates rather than silently reusing an invalid native operation.

No unverified translation of longer routines is claimed. These entry points are a constrained, source-proven *instruction-level* pilot and do not establish correctness of broader PRG control flow. The original strict semantic decompilation coverage ledger is not increased.

## Independent synthetic 6502/hardware parity proof

`JP/decomp/tools/jp0735_original_boot_fixture.py` generates a **wholly invented** Mapper24 cartridge which begins at the same CPU addresses with those standard four 6502 instructions, but fills the intervening original-game PPU status polling path with **ten invented NOPs** and a synthetic JMP loop. No original game's level, title, audio, pixels, or instruction span is copied into the fixture. The production ROM gate never accepts this test image; only a dedicated test-only compile-time bypass allows it.

Linux CI builds two entire independently linked native 6502/Mapper24/PPU/APU executables, one with `JP0735_ENABLE_ORIGINAL_BOOT_NATIVE=OFF`, the other ON, both using the same publicly generated artificial cartridge. The test **requires all four native hit counters nonzero** and compares all fields in twenty complete per-frame `--hash-out` records between interpreted and native execution. The earlier JP0732 and JP0734 synthetic full-frame regressions remain separate.

## Original MesenCE source evidence and authenticity limits

Checked *locally* using the user-provided private original ROM and archived owner MesenCE run `JP0718-20261023-213546-MESEN-RAW-INPUT.zip`:

- The source ROM reset vector and all four opcodes/one immediate are exactly as the table above.
- Original MesenCE's hardware log records CPU **$E02C**, fixed physical $3E02C (PRG-relative, no iNES header), during frame **2** at cycle **57,849**, while original room selector RAM $0035 moves from $03 to $00. This is an independent indication the original boot execution reached initialization **past** the four candidate native sites. It is **not** per-instruction trace parity for those four instructions.
- The original archived run contains **256** screenshots/snapshots and ends on route selector **00/03/00**, at frame **17,472**, with user stop at frame **17,562**.
- The existing JP0719 native replay contains **245** captured snapshots and used the verified original input schedule SHA-256 `27b502aaeca9f5d5381f9f9a812cc188043d083d8ac8b3a89bc40c70f3c30196`. Its final recorded room selector was **00/01/00**, not **00/03/00**. It was produced **before** JP0732–JP0735.
- `JP/decomp/tools/verify_jp0735_original_boot_evidence.py` reproduces the private owner-ROM and archived-capture identity/boot/mismatch checks without extracting or exporting ROM, screenshots, RAM or input logs.

## JP0736 — Actual authenticated Japanese ROM run and forensic MesenCE comparison

The same **ROM-free** JP0735 Linux engine compiled in GitHub CI was downloaded for *private local validation only* (engine ELF SHA-256 `c279d4f9b75d160de3f2c35049b15f40e780bc5852aa6e44488c30871c085fff`). **Neither engine artifact nor any copyrighted original ROM or artwork was added to Git.** The only original runtime input was the already supplied private Japanese ROM; the original archived controller schedule SHA-256 is `27b502aaeca9f5d5381f9f9a812cc188043d083d8ac8b3a89bc40c70f3c30196`.

The native engine was invoked unattended with original media, 17,563 frames, `--edition original --no-save --uncapped --input`, per-frame machine hashes, `--frame-log-at mesen` for the first 1,201 frames and an additional CPU+PPU diagnostic at frame 17,472. Exit code **0**. Source ROM SHA identity check passed before CPU start. Hardware core was `LLE`. Four JP0735 native entries each executed **exactly once**, with eight compiled CPU cycles total. The remaining **523,032,546 guest CPU cycles** executed in the existing interpreter. No stage gameplay was played or recaptured manually.

Comparison used the archived original MesenCE 256 raw screenshots, RAM dumps and PPU dumps. `JP/decomp/tools/jp0736_compare_retail_mesen_frame_log.py` is the ROM-free, reproduction-ready offline comparator (original ROM only used as local hash anchor). For the twelve archived checkpoints at frames 24, 264, 416, 664, 832, 856, 1096, 1128, 1144, 1168, 1184 and 1192:

- Every original logical nametable 1 KiB block finds **zero tile-byte differences** against the corresponding best-matching native physical 1 KiB CIRAM page. The best-page metric is not evidence that every nametable bank selection register is identical; repeated logical pages can map to the same physical page.
- Native color-index classes were mapped to Mesen's RGB values using **one global class-to-RGB lookup for all twelve frames**, not one arbitrary lookup per screenshot. **11 of 12 full native 256×240 pictures match exactly (61,440/61,440 color classes).** Frame 24 differs at **512 pixels**. This is strong picture-class parity, not a bit-identical assertion about different RGB/analog palette encodings.
- Native-vs-Mesen CPU cycle offsets by sampled frame were `[+3,+3,+1,+5,+2,+3,+2,+2,+5,+3,+3,+2]`; CPU RAM differences were `[2,3,21,29,27,20,62,35,45,51,35,44]` of 2,048 bytes. Exact CPU/RAM parity **was not achieved** even early. At frame 24 the two nonmatching RAM offsets were stack-page `$01FC` and `$01FE`.
- At frame 264, 2,045/2,048 CPU RAM bytes matched, and color-class pixels matched 61,440/61,440.

Additional fully automated native CPU/RAM/PPU/color-class comparisons used independent native `--frame-log-at mesen` windows at 1,201–4,000 and 4,001–8,000, with the exact same original controller schedule. Across **98 MesenCE checkpoints through frame 7,968**, **all 98 original $34/$35/$36 room selectors matched the new retail runtime**. The native run transitions through original selector `00/01/01` near frame 4,008 and `00/01/03` by frame 7,336, as the Mesen capture does. This proves the entire early room-selector sequence stays synchronized substantially longer than the first sprite/picture differences.

The first non-512-pixel-class-perfect checks occur at frames 1,816 (2 mismatched pixels), 1,880 (223), and 2,072 (75). The first **substantial** mismatch is at Mesen frame **2,144** (7,671 of 61,440 pixel classes different); frame 2,176 has 8,495 differences. Both frames have *zero best-projected nametable differences* across all four logical 1 KiB blocks, and the PPU palette snapshots differ only at indices `$10,$14,$18,$1C`, which are universal palette alias entries. Frame 2,328 later returns to **zero pixel-class difference**, although some intervening frames differ widely. This is not typical of a permanently incorrect original static room layout; further diagnosis should compare CHR bank timeline, PPU scroll timing, sprite/OAM states and composition across dynamic effects. The first full room-selector divergence is **after** frame 7,968.

**Full-length failure is now confirmed on the new executable**: the 17,563-frame run terminated in **GAME OVER**. At Mesen's original checkpoint frame **17,472**, the original completes Stage 1 and shows route selector `00/03/00`, CPU cycle **520,352,201**, while JP0735 has selector `00/01/00`, CPU cycle **520,352,317** (+116), and **759/2,048 CPU RAM bytes disagree**. At engine exit (frame 17,562), CPU cycle was **523,032,561**. The new limited native boot optimization neither caused an observed early frame/nametable change nor resolved the later replay divergence.

## JP0737 — First progressive gameplay divergence localized with authentic owner media

Two further owner-local unattended JP0735 runs replayed the original recorded controller schedule through native frame 4,000 and frame 13,000, recording only the necessary live `CYCFRAME v2` state windows at frames 1,201–4,000, 4,001–8,000, and 8,001–13,000. All were run with the **identical Japanese SHA256-validated cartridge and native ELF**, without changing the four boot handlers, creating any ROM-derived public asset, or asking the user to replay Stage 1.

Across all **138 archived MesenCE checkpoints up to and including frame 10,272**, the live original/game-room selectors RAM `$34/$35/$36` **agree** with JP0735. The **next original MesenCE checkpoint, frame 10,328, is the first mismatched selector**: original `00/02/01`, native `00/01/02`. Many gameplay scenes and room transitions preceding that mismatch agree in exact selector order.

Source timeline narrows the actual movement failure further inside horizontal source room `00/01/02`:

| Frame | Original Mesen room-local camera RAM $53/$54 | JP0735 native room-local camera | Live selectors both equal? |
| ---: | ---: | ---: | --- |
| 9,312 | $0000 | $0001 | yes |
| 9,376 | $0000 | $0000 | yes |
| 9,440 | $000A (10) | $0009 (9) | yes |
| 9,504 | $0031 (49) | $0030 (48) | yes |
| **9,576** | **$005D (93)** | **$0038 (56)** | yes |
| 9,760 | $00B0 (176) | $0039 (57) | yes |
| 10,272 | $0200 (512) | $01B0 (432) | yes |
| **10,328** | **$0216 (534)** | **$01B6 (438)** | **no** |

Original and native CPU `$18,$19` game-status bytes were still `04,03` on each of those selected checkpoints, with the Stage 1 HUD signature bytes `$5A–$5D=41 84 51 8D` unchanged. The original room continued moving after frame ~9,550, while the native camera temporarily slowed/stalled and never completed the expected room transition in time.

The first large, sustained **in-this-room** graphics mismatch occurs at frame **9,504** (15,249 color-class pixels different); nametable difference there is only **8** best-projected tile bytes, but by frame 9,576 it is **194**, and by frame 9,760 **526**, increasing as room-local world positions diverge. The persistent atlas source crosswalk need not be wrong to produce those discrepancies: the two games are rendering *different positions/objects* from a game state that is already becoming desynchronized.

Archived original input pulses in that window include Down+Right near 9,388–9,450, a Left correction around 9,493, then repeated A/B+Right inputs from approximately 9,536–9,550. These are source-derived timing observations, **not** proof that the controller implementation is broken. The next debugging target is the **first movement/object-state divergence in frames 9,440–9,576**, especially player hitboxes/collision, sprite/OAM, input latch/read phase, dynamic CHR switching, and scroll-boundary transition conditions. Do not introduce speculative gameplay patches or credit more native semantic bytes on the basis of screenshots alone.

The **later** full-run mismatch at frame 17,472 (original 00/03/00; native 00/01/00) is downstream of this first proven transition divergence. Original software rendering/picture parity remains strong at many earlier checkpoints; this does not prove all timing and object state are cycle-perfect.

**Engineering conclusion:** Authentic original-game CPU/PPU/pixel agreement is excellent in the initial sampled section, but the later controller-driven stage progression still diverges. Further native-handler coverage must not be used to paper over that behavioral discrepancy. The next work is locating the **earliest** gameplay-state divergence with sparse original Mesen checkpoints and analyzing controller sampling, timing, and game object state, without requiring another manual Stage 1 playthrough.

Private runtime captures and borrowed diagnostic engine were used locally only. No raw ROM or extracted game data distributed.

VPP remains **31/100**, strict original semantic PRG coverage **49,504/262,144**.
