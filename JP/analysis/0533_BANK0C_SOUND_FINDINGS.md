# 0533 — Raw bank0C sound interpreter and indexed source metadata

Authenticated original **Japanese** Mapper 24 VRC6 ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

This pass uses the original [04F5 bank0C ROM audit](../tools/audit_nmi_bank0c_zp10.py), which proved a 1,488-instruction-start bounded control-flow graph across $8000–$91FF and six original indirect-dispatch sites. The 0532 bank04/05/0C common parser already held 786 starts; 0533 recovers **702 additional original 6502 instructions / 1,599 opcode-and-operand bytes** outside the shared parser. No speculative linear sweep was used.

The original sound metadata index at bank0C CPU $8F60 has **125 source-indexed pointer words** ($8F60–$9059, 250 B) addressing **125 bounded records** ($905A–$9540, 1,255 B). Of these, 79 records select bank0C, 17 bank04, 14 bank05, and 15 are distinct 4-byte bank00 variants. The counted triplet records contain **325 producer references**: 139 bank0C, 102 bank04, 84 bank05. Bank0C references name **125 distinct sound roots** $9541–$A303. The producer-addressed pool $9541–$A303 is 3,523 bytes; it is **sound data, not executable 6502 code**. Full individual command semantics and the apparent adjacent $A304+ pointer table remain open.

Physical original ROM source checks:
- 04F5 bank0C $8000–$91FF SHA256 `2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734`.
- 04F6 bank0C $9200–$9FFF SHA256 `d7387b04a03289ebb1a0567ef49240d90b0bb177a0c128c8b06dbccabdb0776f`.
- Metadata $8F60–$9540 SHA256 `ff50c2a4cd6273ca001535a5e319a68526b7e0b7a1ab173b2ced00f5a32f7154`.
- Producer-rooted bank0C pool $9541–$A303 SHA256 `0df689b5769e50d65d736abe77cbe5752c2b6980de172164991ef32f78d38721`.

| PRG classification | 0532 | New 0533 | Cumulative |
|---|---:|---:|---:|
| Original 6502 instruction bytes | 12,294 | 1,599 | **13,893** |
| Dispatch/parser-local/typed metadata | 907 | 1,505 | **2,412** |
| Earlier authenticated bank04/05 script source | 28,200 | 0 | 28,200 |
| New producer-rooted bank0C pool | 0 | 3,523 | 3,523 |
| **Total classified** | **41,401** | **6,627** | **48,028** |
| Unclassified PRG | 220,743 | -6,627 | **214,116** |

All 25 generated PRG/CHR bank-source files reassemble byte-for-byte to the exact original **393,232-byte** Japanese iNES ROM locally. Four negative tests mutate an authenticated interpreter opcode, metadata index, descriptor, and terminal sound root; all are rejected. The retail ROM and generated copyright-bearing bank source are distributed only in the local user archive, not committed.

Commands:
```sh
python3 JP/tools/test_bank0c_sound_0533.py
python3 JP/tools/test_bank0c_sound_0533.py --rom "$ORIGINAL_JP_ROM"
python3 JP/tools/build_whole_cart_recomp_0529.py --rom "$ORIGINAL_JP_ROM" --out /tmp/jp0533
```

**No new strict credit** is claimed for source classification. Strict PRG remains **49,504/262,144** bytes, VPP **27/100**, original semantic checkpoint **0508**, fixed frontier **$FB96**. The source pool is not fully decoded command-by-command, and no playable native or independent original-Mesen parity is claimed.
