# 0526 — Original Japanese PRG history recovery and symbolic 6502 recompilation

Original retail JP ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Original VRC6 Mapper 24. Physical PRG offsets below exclude the 16-byte iNES header.

## Recovered historical certificate

Recovered checkpoint **04FE** (11 independently hashed regions, **957 bytes**) from historic Git `78896c70544bdf926c3f97d29013995a261e1e1a` and corrected checkpoint **04FF** (6 disjoint regions, **931 bytes**) from historic Git `a7d31bf1e7d608fa356b94eb54d4d17c8caa1a50`. The abandoned 1005-byte 04FF bounding window is not substituted for the corrected 931-byte certificate.

| Evidence | Regions | Previously certified physical bytes |
|---|---:|---:|
| 04FE | 11 | 957 |
| Corrected 04FF | 6 | 931 |
| 0500–0508 (0525 audit) | 59 | 6,029 |
| **Known disjoint physical union** | **76** | **7,917** |

The 41,587-byte pre-04FE historical component lacks a complete physical-location manifest; it has not been fabricated or declared disjoint from newer candidate spans. The 0510–0517 source windows remain 1,365 unique bytes: 626 already in recoverable certificates, **739 unresolved** against the older baseline. This is *not* 739 new certified bytes.

Reproduce historical union from the actual JP ROM:
```sh
python3 JP/tools/audit_historical_prg_0526.py --rom "$ORIGINAL_JP_ROM"
```
Without `--rom`, CI deterministically verifies the physical mapping, disjointness, and certificate quantities, but not the original-ROM SHA source bytes.

## Genuine 6502 instruction-level recompilation

The following bank-qualified regions are now represented as original 6502 mnemonic source, with symbolic local labels/branches, external JSR/JMP targets and the original inline three-pointer descriptor table. No source ROM bytes are checked into the repository as a binary.

| Original CPU source | Physical PRG start | Mnemonic/operand/data bytes | Status |
|---|---|---:|---|
| fixed31:$FDE4–$FE62 | $03FDE4 | 127 | exact |
| fixed31:$FE76–$FEE9 | $03FE76 | 116 (including 6 inline data) | exact |
| raw0B:$8161–$8192 | $02C161 | 50 | exact |
| raw0B:$826C–$8281 | $02C26C | 22 | exact |
| **New 0526** | | **315** | **byte-for-byte** |
| 0525 symbolic source | | 88 | exact |
| **Cumulative symbolic source** | | **403** | **byte-for-byte** |

The two-pass `tools/test_recomp_6502_0526.py` assembles original 6502 opcodes and addressing modes, resolves branch targets and cross-region labels, encodes three 16-bit inline `.word` pointers, checks the exact physical source SHA-256 of each of four spans, and optionally compares all assembled bytes to the original retail JP ROM.

```sh
python3 JP/tools/test_recomp_6502_0525.py --rom "$ORIGINAL_JP_ROM"
python3 JP/tools/test_recomp_6502_0526.py --rom "$ORIGINAL_JP_ROM"
```

**Accounting:** Symbolic recompilation, previously credited PRG source coverage, and independent original-Mesen runtime state parity are different achievements. These 315 newly reassembled bytes were already included in strict historical PRG certification; strict **49,504 / 262,144** remains unchanged. VPP **27/100**, certified semantic checkpoint **0508**, fixed physical investigation frontier **$FB96** unchanged. No new original-Mesen comparison performed.

**Next priority:** recover more physical interval history before 04FE and expand the connected bank-qualified scheduler code through its external raw-$0B callbacks, with separately audited genuinely new PRG byte admissions.
