# 0529 — Original Japanese whole-cartridge PRG bank source and 0501 symbolic code lift

## Actual deliverable

`JP/decomp/tools/build_whole_cart_recomp_0529.py` consumes the user-supplied original Japanese retail-ROM image (VRC6 mapper 24, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`). It generates **17 PRG bank source modules** (15 raw 16KiB pages plus two physical fixed 8KiB pages), **8 CHR graphics modules**, and a machine-readable bank manifest. Full bank output is **byte-for-byte reassembled** from these source files into the original 393,232-byte iNES image, including its 16-byte header, 262,144-byte PRG, and 131,072-byte CHR.

The generator reuses both hand-written 0525/0526 mnemonic modules and the existing [0501 original JP ROM audited scheduler bank graph](../tools/audit_nmi_fixed_scheduler_banked.py). It independently follows **2,035 original certified instruction starts**, validates complete byte occupancy of the original 0501 bank09/bank0A/bank0B certified instruction spans, checks the fixed-bank new span inclusion (including its three inline dispatch pointers), and authenticates each original 0501 region against its hardcoded SHA-256. It explicitly preserves the original `$B974` unreachable branch and stops at unlifted bank0B `$E7FB` indirect jump/inline selector sites rather than inventing code.

| Source classification | Bytes |
|---|---:|
| Previously hand-authored original 6502/source | 403 |
| Newly expressed 0501 authenticated 6502 mnemonics | **4,030** |
| **Total symbolically reassembled PRG mnemonic/inline bytes** | **4,433** |
| PRG bytes still emitted as **UNCLASSIFIED `.byte`**, not code | **257,711** |
| CHR original graphics-data bytes emitted as `.byte` | 131,072 |
| Full PRG+CHR bank source roundtrip | **393,216 / 393,216** |
| Entire retail iNES image with header | **393,232 / 393,232** |

Newly expressed instructions: fixed31 47 instructions / 99 bytes; raw09 479 instructions / 1,050 bytes; raw0A 57 instructions / 120 bytes; raw0B 1,281 instructions / 2,761 bytes. The total is **1,864 additional original instruction starts**, not a blind linear disassembly. Original bank0B raw0B actor routines and fixed scheduler remain represented by the human-maintained source where available, not duplicated in the generated output.

## Reproduce and test

```sh
python3 JP/decomp/tools/build_whole_cart_recomp_0529.py --smoke
python3 JP/decomp/tools/build_whole_cart_recomp_0529.py --rom "$ORIGINAL_JP_ROM" --out /tmp/cviii-jp-0529-banks
```

All **25 complete bank source files** are generated locally from the user-provided ROM and are not checked into the repository, because they contain verbatim original copyrighted PRG/CHR data. The source generator and authenticated original 0501 graph audit are tracked in Git. The original-ROM mode runs a two-pass assembler independently over each generated source bank and compares it with every source byte; CI without the ROM runs the assembler smoke and static Python checks.

**No strict PRG certification increase**: the 4,030 new *symbolic* bytes were already authenticated as part of 0501's strict code graph. Previously certified 49,504/262,144 PRG bytes, VPP 27/100, certified semantic checkpoint 0508, and fixed frontier `$FB96` remain unchanged. This source generator is not a playable native CPU/PPU/APU recompiler or original-Mesen frame-parity proof.

Next work: bulk source conversion of additional already-proven 0504 graphs and earlier bank source data formats, and recovering the remaining 27,419-byte historical physical PRG baseline before promoting any candidate unclaimed bytes.