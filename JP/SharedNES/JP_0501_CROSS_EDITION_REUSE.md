# Original-certified JP code regions: exact US correspondence census (0501)

**Date:** 2026-10-09. **Evidence grades:** JP original-ROM **strict 0501 code/operand certification**; US region **C1 exact-byte candidate**, **not** transferred US gameplay liveness or native parity.

## Completed ROM-locked audit

The original Japanese Castlevania III (Mapper 24, VRC6a) 0501 semantic checkpoint admitted **4,364 new, noncontiguous code/operand bytes** in **31 hash-pinned physical PRG regions**. The original 0501 source evidence is [NMI_FIXED_SCHEDULER_BANKED_0501.md](../analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md). The reusable tool [nes_certified_reuse.py](../tools/nes_certified_reuse.py) verifies the original Japanese cartridge SHA, original US cartridge SHA, **all 31 original region SHA-256 fingerprints**, region non-overlap and the 4,364-byte original-source total.

For every fully contained **16-byte exact window**, the tool searches the entire US 256 KiB physical PRG (MMC5 mapper 5), counts only candidates occurring at **one exact US physical offset** as uniquely anchored, separates multiply occurring windows, and does not count bytes in overlapping source windows twice.

| JP certified source domain | JP certified bytes | Source bytes with uniquely matching US windows | Ambiguous-only | Without any matching 16-byte window |
|---|---:|---:|---:|---:|
| Raw VRC6 bank $09 | 1,050 | 263 | 0 | 787 |
| Raw VRC6 bank $0A | 120 | 65 | 0 | 55 |
| Raw VRC6 bank $0B | 2,896 | 879 | 5 | 2,012 |
| Fixed PRG31 | 298 | 66 | 0 | 232 |
| **Total** | **4,364** | **1,273 (29.17%)** | **5** | **3,086** |

All quantities describe **distinct bytes already credited to the Japanese 0501 ledger**, not newly verified US or JP code. A region can contain multiple non-overlapping exact windows and different US offsets. No target instruction-start boundary, call graph, bank mapping, or mapper-side effect is automatically certified by exact bytes. The 16-byte window threshold is a matching *heuristic*, not a semantic identity threshold. US-specific hardware is MMC5, while JP hardware is VRC6; mapper equivalence must be established separately.

Notable examples for targeted US verification:

- JP raw $0B:$8001–$804A has **73/74** source bytes covered by unique windows and its **entire 74-byte strict region** matches a US physical span at the same PRG offset $2C001.
- JP raw $09:$8692–$86BD has a **44-byte exact source span** at US physical PRG offset $2473A; the US CPU context is not inferred from this offset.
- The already independently documented JP fixed $E7FB → US physical $E86D dispatcher [C1 routine anchor](JP_US_DISPATCH_EXACT_MATCH.md) is a separate 25-byte/15-instruction match not part of this strict-0501 census.

## Portable method

This tool accepts **any NES ROM pair** with supported cartridge headers and any compatible hash-only source-provenance manifest, regardless of publisher or mapper. It can be reused for future Konami, Capcom, Nintendo or other titles only when an original game supplies independently certified source spans. The source manifest for this example is [JP_0501_CERTIFIED_REGIONS.json](JP_0501_CERTIFIED_REGIONS.json); the generated complete hash/offset-only report is [JP_0501_CROSSROM_CENSUS.json](../analysis/JP_0501_CROSSROM_CENSUS.json).

```sh
python3 JP/tools/nes_certified_reuse.py '/private/japan.nes' '/private/usa.nes' JP/SharedNES/JP_0501_CERTIFIED_REGIONS.json --window 16 --out /tmp/crossrom.json
python3 JP/tests/test_nes_certified_reuse.py
# Optional full original pair integration (ROM files stay private)
NES_REUSE_JP_ROM='/private/japan.nes' NES_REUSE_US_ROM='/private/usa.nes' python3 JP/tests/test_nes_certified_reuse.py
```

**Tests:** 18 synthetic/evidence tests total; 17 ROM-free passed in CI and 1 optional exact JP/US pair check passed locally. **No original ROM/BIOS/content payload committed.** Strict semantic PRG remains **49,404/262,144 (18.8461%)**, VPP **25/100**, completed semantic checkpoint **0507**, fixed PRG31 frontier **$FB96**. The original US mapping/caller proof and original emulator reference traces remain open.
