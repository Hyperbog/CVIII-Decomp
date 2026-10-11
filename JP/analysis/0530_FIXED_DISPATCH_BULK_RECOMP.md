# 0530 — Bulk fixed-bank 04FE/04FF/0500 original 6502 dispatch source

Original Japanese Akumajou Densetsu VRC6 (mapper24), ROM SHA256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Source procedure uses the original independently certified physical PRG31 fixed bank located at original PRG offset $03E000-$03FFFF. All original ROM bytes and CRC are verified locally but not committed.

## Source-graph restoration

`JP/tools/lift_fixed_dispatch_0530.py` extends the [0529 original 0501 whole-cart assembler](../tools/build_whole_cart_recomp_0529.py) using three **historically authenticated** graph sets, not a speculative linear disassembly:

| Original evidence checkpoint | Source bytes in historical fixed bank manifest | Control-flow reconstruction |
|---|---:|---|
| 04FE | 957 | E363 first-level 16-pointer dispatch, original 435 instruction starts plus independently certified E7FB dispatcher body |
| 04FF | 931 | F39D 32-pointer nested dispatch; exactly 401 original instruction starts / 931 instruction-and-operand bytes |
| 0500 | 982 | Original F84E 16-pointer and F96A 10-pointer secondary dispatch; 414 original instruction starts plus explicit 58 bytes of tables |

The decoder independently authenticates all 23 disjoint original fixed-bank certificate spans using their original per-interval SHA-256; confirms exact original pointer tables and branch boundaries; rejects instruction fragments not wholly inside those admitted spans; checks that reconstructed instruction/data coverage of **each** stage equals its source-mapped certificate byte-for-byte. Legacy script source and 0501 mapping are not inflated into new 6502 code.

The 0530 new **source classification**, disjoint from 0529 original source:

- 1,218 additional certified original instruction starts.
- **2,719 additional opcode/operand bytes**, now real NMOS 6502 mnemonics.
- **154 additional typed pointer table bytes**, expressed using `.word` entries and symbolic labels.
- **2,873 total** newly meaningful source bytes.
- Cumulative **7,306 / 262,144 PRG source bytes** explicitly reassembled as known code or bounded typed tables: **7,146 instruction bytes** and **160 inline pointer-table bytes**.

## Whole cartridge evidence

The generator emits 17 complete PRG bank sources (15 switchable 16KiB and two fixed 8KiB regions) plus 8 CHR 16KiB original graphics sources. The rest of PRG remains labeled *UNCLASSIFIED* and emitted as original source `.byte` fallback. Every bank is separately assembled from its generated source then the original 16-byte iNES header, 256KiB PRG and 128KiB CHR are recombined and compared byte-for-byte to the original retail Japanese image:

- **393,232 / 393,232 bytes exact**, SHA256 original verified.
- Total symbolic/typed 7,306, unclassified PRG **254,838**.
- CHR 131,072 remains structured as original graphics byte sources, *not* 6502 code.

Reproduce:

```sh
python3 JP/tools/build_whole_cart_recomp_0529.py --smoke
python3 JP/tools/build_whole_cart_recomp_0529.py --rom "$ORIGINAL_JP_ROM" --out /tmp/cviii-0530-whole
```

The original retail ROM remains an external input. Generated cartridge-bearing bank files must not be committed.

**Certification boundary:** 2,873 newly *expressed* source bytes were already present in historic strict 04FE, 04FF, and 0500 evidence; **no new strict PRG byte credit**, no independent original-Mesen parity assertion, no VPP promotion. Strict floor 49,504 / 262,144, VPP 27/100, semantic certificate 0508, and fixed investigation frontier FB96 remain unchanged.

Next large work unit: original 0504 raw0B/fixed31 code/data graph and the bank05 original script command + operand structure, as separate code versus data classifications.