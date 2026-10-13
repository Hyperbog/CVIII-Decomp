# JP 0593 — Japanese password / stage-selector foundation

The user requested an in-game level-selection debug menu. The retail game's native password decoder offers a safer stage-transition path than unverified mid-frame writes to gameplay RAM. This phase isolates the first prerequisite: reconstructing the ROM-grounded *password tables* and providing a separately testable codec. **It does not yet install an F10 in-game warp menu.**

## Authentication and physical addresses

Original Japanese mapper24 ROM: SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. File contains a 16-byte iNES header, 256 KiB PRG, and 128 KiB CHR. Python tool `JP/tools/jp_password_stage_0593.py` refuses a different ROM and reads six byte-exact tables from original physical PRG:

| Table | Physical 8 KiB PRG bank | PRG offset | Length |
|---|---:|---:|---:|
| Password scramble chains | 03 | 0x078DD | 27 |
| Name-hash seeds | 03 | 0x07911 | 8 |
| Nine save-point selectors | 03 | 0x07B62 | 9 |
| Three scramble leaders | 03 | 0x07A0A | 3 |
| Partner-availability bits | 03 | 0x07AE1 | 6 |
| Block-to-save-point map | 00 | 0x00EF1 | 45 |

These six complete tables are byte-identical to the respective North American tables at *different* physical positions; JP code near physical PRG offset 0x0791E refers to save-point RAM `$0030`, not the US `$002E`. This confirms shared layout, but **not yet complete JP decoder control-flow or game acceptance**. Do not substitute US ROM execution for Japanese original-game parity.

## Local original-ROM tests

```sh
python3 JP/tools/jp_password_stage_0593.py --rom "/private/Akumajou Densetsu (Japan).nes" --self-test --list
python3 JP/tools/jp_password_stage_0593.py --rom "/private/Akumajou Densetsu (Japan).nes" --stage 5 --partner sypha --name TREVOR
```

The first implementation passed 952 internal round trips across four names, 18 checkpoints, four partner states, two difficulties, and both scramble masks (excluding disallowed combinations), including wrong-name rejection. This proves internal codec consistency with the authenticated table bytes; it **does not prove** the actual Japanese game accepts every generated password. Names and route labels derive from the published North American password analysis (Meat Fighter, https://meatfighter.com/castlevania3-password/), explicitly presented there as not independently applicable to JP. Record separate ROM-backed acceptance before enabling a debug warp.

## Next bounded delivery

Trace the original JP password submission/confirmation and its transition into stage initialization using an independent reference emulator. Confirm `$0030`, partner/mode variables, valid stage/route load and post-load CPU/PPU/mapper/IRQ state. Add a paused, debug-only F10 stage picker in the private SDL host. Select a verified checkpoint, request the original game password path through an independently tested host hook, and compare against manually entered password save point by save point. Keep Original/Enhanced machine semantics identical; no hardcoded gameplay RAM pokes, no ROM copies, no false PRG/VPP promotion.

Current strict PRG 49,504/262,144 and VPP 27/100 unchanged. Semantic checkpoint 0508 / frontier PRG31 $FB96 unchanged.
