# 0508: Physical PRG CDL bridge and ROM-cross-edition candidate census

**Evidence classification:** authentic input images verified by SHA-256; executable CPU paths in these audits are **synthetic models with manually injected NMIs**, NOT independent original-reference emulator gameplay. No code/data logger input from FCEUX/Mesen was supplied for this test. No ROM bytes are distributed or promoted to the strict ledger.

## Implemented format converter

- [FCEUX documented CDL flags](https://fceux.com/web/help/CodeDataLogger.html): 1 code; 2 data; 4/8 last mapped CPU window; 16 indirect code target; 32 indirect data read; 64 PCM; 128 reserved.
- [Mesen1 distinction](https://forums.nesdev.org/viewtopic.php?p=283235): similar basic flags, but indirect and bit 7 semantics may differ. Raw headerless files cannot be reliably distinguished just from the bytes.
- [Mesen2 source](https://github.com/SourMesen/Mesen2/blob/master/Core/Debugger/CodeDataLogger.cpp) and [header size](https://github.com/SourMesen/Mesen2/blob/master/Core/Debugger/CodeDataLogger.h): **CDLv2 + uint32 ROM CRC** header (9 bytes), then physical memory flags. Header CRC without independently known expected value is recorded as **unverified**, not treated as proof of cartridge identity.
- Physical 8-KiB bank breakdown, file SHA-256 and per-region original-ROM hash checks; full input mask **not committed**. A CDL code bit is observed execution only; it never proves global reachability. Unmarked bytes are not proved unreachable.

## JP original-ROM synthetic model and cross-edition results

| Metric | Value |
|---|---:|
| Input model trajectories | start30, 300 manually injected NMIs; no input, 120 NMIs |
| JP 6502 instruction executions | **1,061,384** |
| Distinct physical PRG instruction/operand bytes observed | **4,979** |
| Additional read-only PRG bytes in synthetic aggregate | **2,454** |
| Active 8-KiB physical PRG code banks | 00, 03, 08, 24, 26, 31 |
| Previously certified checkpoint-0501 source byte intervals | 31 regions, **4,364** bytes |
| 0501 source bytes observed in either synthetic trace | **0** |
| Modeled code-bit runs at least 16 bytes long | 86 runs, **4,515** bytes |
| Eligible code-run source bytes with unique exact US windows | **909** |
| Source bytes with ambiguous-only US windows | 146 |
| Source bytes without 16-byte exact US matches | 3,460 |
| Shorter-than-16 code-run bytes (excluded) | 464 |
| Newly strictly verified JP PRG bytes | **0** |
| VPP increase | **0** |

**Distinct code-run counts are not independent verified routine counts.** These two limited simulated trajectories primarily cover early boot/menu paths; they do not visit the already-semantic-verified 0501 object scheduler intervals, which explains part of the persistent failure to reach the targeted world/room state. The checkpoint-0501 manifest is only a subset of the complete 0507 strict coverage ledger; other overlaps must not be guessed.

### Concrete 50-instruction same-code candidate

JP **PRG31 offset $3E7B8–$3E813**, potentially CPU **$E7B8–$E813** in the fixed JP mapper-24 last window, is 92 contiguous executed-code/operand-marked bytes in the tested synthetic paths and linearly decodes into **50 official 6502 instructions**, SHA-256 `46cdf98916b346b5da7217e310cbe7d17a6ecd0dec5e1a631111e9364a570094`. The US physical PRG31 offset **$3E82A–$3E885** contains **the same 92 bytes**, uniquely. It includes the previously audited 25-byte inline dispatcher JP $E7FB ↔ US candidate $E86D.

This **extends candidate exact-code correspondence**; it does not establish a live MMC5 US CPU bank context, a caller, side-effect domain, source-code identity or any new strict PRG byte credit. [Earlier 25-byte anchor](JP_US_DISPATCH_EXACT_MATCH.md) and [source certified 0501 census](JP_0501_CROSS_EDITION_REUSE.md) remain different evidence types.

## Reproduction

```sh
python3 JP/tools/audit_0508_cdl_trace_bridge.py '<JP ROM>' JP/SharedNES/JP_0501_CERTIFIED_REGIONS.json /tmp/model-cdl-summary.json
python3 JP/tools/audit_0508_synthetic_crossedition_0501.py '<JP ROM>' '<US ROM>' JP/SharedNES/JP_0501_CERTIFIED_REGIONS.json /tmp/model-cross-edition-full.json
python3 JP/tests/test_nes_cdl_bridge_0508.py
python3 JP/tests/test_synthetic_crossedition_0508.py
```

The full audit report is deterministic and machine-generatable from the two legally provided images; the compact committed summary contains the key metrics and hashes. No full 262,144-byte CDL mask or lossless disassembly is committed.

**Current project accounting remains VPP 25/100, strictly covered PRG 49,404/262,144 = 18.8461%, last completed checkpoint 0507, fixed PRG31 frontier $FB96.** The next required source of actual progress is a real external emulator CDL/CPU log or full PPU/IRQ producer proof, not another synthetic selector-only extension.
