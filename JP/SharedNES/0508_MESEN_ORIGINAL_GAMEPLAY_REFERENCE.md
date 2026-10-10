# 0508: Independent Mesen original-JP-ROM gameplay witness and physical PRG CDL

**Evidence class:** independently emulated original-ROM frame execution; **not** project-CPU/reference cycle-by-cycle equivalence, a full semantic dependency closure, or a finalized 0508 checkpoint. This is materially stronger than earlier synthetic-NMI/PPUSTATUS state-injection studies. Japanese ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (iNES 393,232 bytes, VRC6a/mapper 24, 256 KiB PRG, 128 KiB CHR). The ROM **never** leaves the private analysis environment. No complete Mesen CDL, instruction trace, screenshots, save states, PRG banks or original ROM data are committed.

## Independent emulator acquisition / provenance

External project: [atonamy/mesen-agent](https://github.com/atonamy/mesen-agent), release [`v0.1.0`](https://github.com/atonamy/mesen-agent/releases/tag/v0.1.0), using independently maintained **Mesen2 v2.1.1** core under the release's published GPL terms. `JP/.github` workflow [Prepare Independent Mesen Reference CLI](../../.github/workflows/jp-reference-agent-bundle.yml) fetched the Linux x64 bundle with its upstream `SHA256SUMS` and published a **one-day emulator-only** GitHub Actions artifact; upstream archive SHA-256 `bff3c1d31a4b5ae5322b075330eccb3e78e96050d7a4e593c02804d8f1de7ae2`. Extracted executable SHA-256 `95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0`; core shared library SHA-256 `fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1`. Emulation identified the correct NES VRC6 cartridge and resumed reset-derived game screens. Emulator binary/core are research dependencies, **not** our native port or a ROM payload.

Mesen's debugger [Lua API](https://github.com/SourMesen/Mesen2/blob/master/UI/Debugger/Documentation/LuaDocumentation.json) reads RAM `$18/$19/$68/$2C/$07A0/$07A6` at the *end* of each emulated video frame. Reproducible script: [`../tools/mesen_0508_frame_state.lua`](../tools/mesen_0508_frame_state.lua). `--save-cdl NesPrgRom=...` outputs `CDLv2` 9-byte header, then a 262,144-byte physical PRG flag mask and 131,072-byte CHR flag mask. It is consumed only **locally**; compact hashes, counts and the sampled state sequence are emitted by [`../tools/audit_mesen_reference_0508.py`](../tools/audit_mesen_reference_0508.py). CDL flags 1=code, 2=data are observations, not complete reachability proofs. Physical PRG bank layout is determined by Mesen from each actual mapper-selected fetch.

## Reproducible 1,100-frame full pregame-to-playable route

The tester runs the exact Japanese source image (not US mapper 5). Inputs use relative frame coordinates of each program stage. Run from a private folder with `mesen-agent` and `MesenCore.so` from the SHA-pinned release, a distinct `--home` per stage, and locally retained (uncommitted) savestates:

```sh
# Part 1: intro -> title -> name entry (520 frames)
mesen-agent "$JP_ROM" --home "$TEMP/gameA" --frames 520 \
  --input '0:start@90-92' --input '0:start@180-182' \
  --input '0:start@300-302' --input '0:right@370-520' \
  --input '0:a@460-469' --input '0:b@470-475' \
  --lua JP/tools/mesen_0508_frame_state.lua \
  --save-cdl "NesPrgRom=$TEMP/play520.cdl" --save-state "$TEMP/play520.mss" \
  > "$TEMP/play520.jsonl"

# Part 2: press START to conclude name entry -> introduction/prayer (220 frames)
mesen-agent "$JP_ROM" --home "$TEMP/gameB" --load-state "$TEMP/play520.mss" \
  --frames 220 --input '0:start@10-11' --input '0:right@125-210' \
  --input '0:b@130-132' --lua JP/tools/mesen_0508_frame_state.lua \
  --save-cdl "NesPrgRom=$TEMP/stage220.cdl" --save-state "$TEMP/stage220.mss" \
  > "$TEMP/stage220.jsonl"

# Part 3: press START to skip/finish prayer -> Stage 1 (360 frames)
mesen-agent "$JP_ROM" --home "$TEMP/gameC" --load-state "$TEMP/stage220.mss" \
  --frames 360 --input '0:start@5-6' --input '0:right@90-325' \
  --input '0:b@130-132' --input '0:a@270-272' \
  --lua JP/tools/mesen_0508_frame_state.lua --screenshot "$TEMP/stage360.png" \
  --save-cdl "NesPrgRom=$TEMP/stage360.cdl" --save-state "$TEMP/stage360.mss" \
  > "$TEMP/stage360.jsonl"

python3 JP/tools/audit_mesen_reference_0508.py "$JP_ROM" \
  --emulator "$MESEN_BIN_DIR" \
  --run play520 "$TEMP/play520.cdl" "$TEMP/play520.jsonl" \
  --run stage220 "$TEMP/stage220.cdl" "$TEMP/stage220.jsonl" \
  --run stage360 "$TEMP/stage360.cdl" "$TEMP/stage360.jsonl" \
  --screenshot "$TEMP/stage360.png" --out "$TEMP/hash-only-report.json"
```

Documented input behavior was cross-checked against [Castlevania III original manual, name-entry instructions](https://www.world-of-nintendo.com/manuals/nes/castlevania_3_dracul_curs.shtml): selecting **END** or pressing **START** concludes name entry. That one manual detail **resolved** the prior apparent state `$0A/$19=03` bottleneck. The screenshots were reviewed privately: end of Part 1 is the **ENTER YOUR NAME** keyboard; end of Part 2 is the church/prayer scene; end of Part 3 is **playable Stage 1** (HUD `BLK 1-01`, player and enemies rendered). Screenshots are **not** included in the repository.

## Actual original-JP execution and physical coverage

| Sequential savestate-connected segment | Frames | Observed PRG executed-code bytes | Observed PRG data bytes | Already certified checkpoint-0501 code bytes executed |
|---|---:|---:|---:|---:|
| Title/name entry (`play520`) | 520 | 5,536 | 2,666 | 0 |
| Name-completion/prayer (`stage220`) | 220 | 5,194 | 1,382 | 0 |
| Stage 1 game (`stage360`) | 360 | 9,352 | 4,361 | **463** |
| **Physical-byte union across all three** | **1,100 frames** | **12,885 distinct bytes** | **7,890 distinct bytes** | **463 distinct bytes, already counted** |

Full union has **20,775 distinct code-or-data-marked PRG bytes**, from **17 physical 8-KiB PRG banks** with code bits (PRG00,03,04,05,08,10,15,20,22,23,24,26,27,28,29,30,31). The exact physical masks and original ROM remain local; the audit emits 32-bank count vectors and SHA-256 mask fingerprints, not a lossless ROM listing or CDL. The **463** known overlap bytes were in the independent checkpoint 0501 **4,364-byte / 31-region** verified scheduler subset ([source manifest](JP_0501_CERTIFIED_REGIONS.json)); even though Mesen executes them, they **must not be counted again**. Other overlap with the full 0507 **49,404-byte** semantic ledger is not yet subtracted: **do not promote the remaining 12,422 observed code bytes by arithmetic**.

Sampled first-level `$18` progression from authentic emulation: **`$00 → $02 → $0A → $09 → $03 → $04`**. On the playable Stage 1 screen `$18=$04`, `$19=$00`, `$2C=$03`; therefore `$18=$04` is **genuine gameplay**, not proof that the CPU is wedged. State `$18=$0C/$0D`, plus the conditional bank-$0A room-loader root, was *not observed in these scenarios* and remains an explicit producer/liveness obligation. Per-frame samples are not instruction-level last-writer proof. The first frame's RAM snapshot can reflect pre-reset/uninitialized emulator memory; analysis ignores it for state liveness.

In a separate 12-frame replay from the private prayer snapshot, Mesen debugger Lua write callbacks observed original ROM writes to selector `$18`, `$19`, `$2C`, `$07A0`, `$07A6` and mapper registers `$8000,$C000,$D000,$F000,$F001`. The callback-observed `$8000` select count was **298** during those 12 frames; that count is **not** a distinct routine count, and the Lua state API did **not** provide a valid PC inside the write callback, so no PC provenance is claimed from it. A raw 111,259-line Mesen instruction trace was produced privately but never added to the repository. This witness establishes genuine ongoing game code and mapper activity, not original-vs-reimplementation cycle parity.

## Certification boundaries / forward conversion target

- **Strong, new independent evidence:** original JP ROM reaches actual Stage 1 screen under controller input and accurate video, code/data logging maps physical PRG fetches, and 463 already-certified scheduler bytes execute in an authenticated path.
- **Not yet established:** full instruction-aligned manifest for every newly observed byte, the complete 0507 overlap ledger, coverage for unobserved game branches and rooms, original vs our native frame/IRQ/audio register parity, or transitive bank state/producer domains for $18=$0C/$0D. Neither a 20,775-byte code/data mask nor screenshots alone establish semantic decompilation completeness.
- **Counts remain unchanged until separate admission:** strict JP verified PRG **49,404/262,144 = 18.8461%**; VPP **26/100**; last fully certified semantic checkpoint **0507**; fixed PRG31 frontier **$FB96**. New strict bytes credited by this evidence report **0**.

**Next large batch:** derive full 0507 credited physical-byte manifest; intersect it with the 12,885 genuinely executed original-JP code bytes; trace exact per-instruction bank context, selector writers and game-input chronology; certify genuinely new unique code/data ranges and native Stage 1 frame parity only after reference timing and branch/domain evidence. Reuse this Mesen run framework for other legally provided Konami/NES/FDS games without assuming shared engine semantics.
