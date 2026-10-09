# Permanent technical discovery and behavior log

**Status:** ACTIVE. This is a readable, append-only *index* of major findings. It is not a substitute for physical byte manifests, the machine [resume state](../analysis/RESUME_STATE.json), or the narrative [subsystem chapters](README.md). All source claims must be rechecked against the immutable Japanese ROM and their linked audits.

## Historical checkpoint-to-behavior index

| Checkpoints | Technical discovery/behavior | Evidence |
|---|---|---|
| 04F2–04F4 | IRQ has 45 encoded states; fixed NMI and ED46 helper examined for shared-ZP preservation | [IRQ](../analysis/PRG02_IRQ_dispatch.md), [fixed NMI](../analysis/NMI_FIXED_ZP10_PRESERVATION.md) |
| 04F5–04FA | Bank $0C sound parser and raw bank $04 metadata parser, 96/96 roots; stream parameter bytes kept as data | [bank $0C](../analysis/NMI_BANK0C_PARSER_MODE.md), [raw $04](../analysis/NMI_BANK04_ALT_PARSER_BOUNDARY.md) |
| 04FB–04FD | Raw bank $05 sound parser, 72/72 roots; E7 index restricted by actual producer | [raw $05](../analysis/NMI_BANK05_PRG11_TAIL.md) |
| 04FE–0500 | $E7FB pops the JSR return and tail-jumps through inline pointers; $18/$2C/$68 encoded dispatches mapped with live-domain caveats | [E7FB ABI](../analysis/NMI_FIXED_E7FB_DISPATCH.md), [$68](../analysis/NMI_FIXED_68_DISPATCH.md) |
| 0501–0502 | Object scheduler calls banked collision paths; seven real bank-$0B ZP $10 writes; exhaustive native 8-bit collision math | [scheduler](../analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md), [scratch](../analysis/NMI_BANK0B_COLLISION_ZP10_0502.md) |
| 0503–0504 | $BD11 AI-script interpreter; producer-backed script ID $1B, actions $0B/$45/$46; fixed $FC1F contributes five more ZP $10 writes | [script seed](../analysis/RAW0B_AI_SCRIPT_SEED_0504.md), [AI decoder](../analysis/RAW0B_AI_DISPATCH_NATIVE_0503.md) |
| 0505–0506 | Distinct $FD62,Y data index domain stays unproved; fixed $FB96 temporarily banks raw $0E, reads indirect and restores $0A; raw-$0A room state candidate transition | [fixed lookup](../analysis/FIXED_TILE_PROBE_0505.md), [banked loader](../analysis/CROSSBANK_AI_ATLAS_0506.md) |
| 0507 | Fixed NMI $E526 selects raw bank $0A and jumps $B4CC; exactly five new verified entry bytes; 281 starts/582-byte room graph remains conditional | [0507 JP proof](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md) |

At 0507, conservative strict PRG floor is **49,404 / 262,144 (18.8461%)** and VPP is **24/100**. These are a historical snapshot, not a live metric. [PROGRESS.md](../docs/PROGRESS.md) and [RESUME_STATE](../analysis/RESUME_STATE.json) own current values.

## Negative discoveries and hypothesis corrections to preserve

- **C-001 (checkpoint 0500):** accounting error (933 vs 982 bytes) was fixed after recovering $F800-$F830; a *tooling mistake*, not a game bug.
- **Q-001:** The $E7FB inline dispatcher *intentionally* consumes its caller's JSR return and pointer literals.
- **Q-002:** ZP $10 is inherited by compressed sprite descriptors, but later collision/background code also writes to it; local audio-path preservation does not imply whole-frame preservation.
- **L-001:** Mechanical action $9E maps into script pointer/fallback data at $BEA3/$BF79; treating all 256 action words as live executable handlers would be false.
- **D-001:** Script IDs $24/$25/$26 have mechanically corresponding actions but no proved live script-ID producers; some tempting immediate values write unrelated RAM fields.
- **U-004 (separate domain):** $FD62,Y must not be limited to the modulo-12 $FD4D,Y index just because the reads share a helper.

See [Q/D/L/C/U register](10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md) for canonical ownership and current unknown status.

## Future update template

For each **completed** checkpoint, append:

1. Checkpoint ID, branch commit and authoritative ROM SHA.
2. Original machine fact — physical 8-KiB PRG / raw bank, CPU start/end and code/data classification; producer → parser/handler → consumer; register, stack, mapper/PPU/APU effects.
3. Evidence grade and reproduction command; distinguish static CFG, strict accounted byte manifest, native unit test and reference-emulator parity.
4. Corrections/contradictions, negative findings, Q/D/L/C/U IDs changed, R-IDs affected.
5. Strict new unique PRG bytes, strict cumulative PRG and VPP *without recounting*.
6. Exact next unknown and its proof requirement.

The owning chapter, this log, and the relevant Q/D/L/C/U entry should be updated in the same **semantic checkpoint** before progress/continuity, with the machine resume state **last**. Editing archival prose alone earns zero ROM bytes and zero parity points.

**Documentation adoption (separate zero-byte transaction):** modeled on the private [RLOFT PreservationArchive](https://github.com/Hyperbog/RLOFT/tree/code1-decompilation/PreservationArchive), while original JP bytes remain authority. No static archive completion certificate and no full native parity are claimed.
