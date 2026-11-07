# JP0833 — Original-JP Stage 1 actor lifetime differential gate

**Target:** the owner-supplied *Akumajou Densetsu* Japanese Mapper24 ROM, SHA256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. No cartridge, proprietary code bytes or private trace is committed.

## Verified now

- Local original-ROM check: physical raw0A, raw0B, raw0F digests and four original movement/damage/sound code-window digests match.
- Original Stage 1-02 selector `00/01/00`, root `$93E8`: rows `00,00,00,32,32,00`; source event PCs `$A444/$A43F` at phases 3/4, room coordinates (160,80)/(192,176), type `$3D`. Chapel `$AB1F-$AB5E` SHA matches independently.
- Public archived original Mesen 2.1.1 reference `JP/decomp/analysis/0509_MESEN_ACTOR_LIVE_REPORT.json` records original controller-reached frame3092 and CPU creation in slots 1 and 2. The current task did not re-run Mesen or produce a new natural trace.
- Synthetic `jp0833_stage1_lifetime_diff.py --smoke` checks both source-parent slots, detects actor disappearance in a paired frame, and rejects different controller poll epoch fingerprints.
- Reactivated JP0827 original-6502 actor VM and JP0828 detached movement/C11 sanitizer gates on the sole `decompilation` branch. These gates exercise synthetic/in-process behavior only.

## Private paired reference execution

For real *frame-by-frame* differential validation, collect 2KiB CPU RAM snapshots from **unmodified original Mesen** and the **native NESRecomp** at identical **post-frame** boundaries, using the identical complete controller-poll input sequence. Keep both files and the ROM in a private directory. Format for each JSONL trace:

```json
{"schema":"CVIII-JP0833-actor-postframe/v1","source":"mesen","rom_sha256":"958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28","boundary":"post-frame","input_sha256":"<64-lowercase-hex SHA256 of the SAME controller poll input stream>"}
{"frame":3092,"ram_hex":"<4096 lowercase hex digits representing exactly 2048 original internal CPU RAM bytes>"}
```

The native trace uses the same header, except `source` is `native`. Each file needs at least two strictly increasing and identical Stage 1-02 frame indices. A mismatched poll SHA or frame set **fails closed**. This is an explicit interoperable export format, not a claim that the existing Mesen/NESRecomp tools automatically output it.

```sh
python3 JP/recomp/tools/jp0833_stage1_lifetime_diff.py --smoke
python3 JP/recomp/tools/jp0833_stage1_lifetime_diff.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --mesen-frames /private/mesen_postframe.jsonl \
  --native-frames /private/native_postframe.jsonl \
  --report /private/stage1_lifetime_diff.json
```

The comparator checks original stage/room/camera/source-slot state plus every 1..12 actor slot's type, parent source, flags, sprite frame, XY, subpixel and velocity-related fields. It returns a nonzero exit on sampled mismatches, refuses mismatched poll histories, and never uploads game data. Counts are sampled allocations only; no frame snapshots can prove intervening CPU writer identity, a true offscreen survivor, contact/$B525 defeat, damage, score or complete 6502/PPU/APU parity. The original reference and native trace inputs were **not available together** in this task environment, so no live paired differential pass is claimed.

**Existing strict certificate and VPP are unchanged.**
