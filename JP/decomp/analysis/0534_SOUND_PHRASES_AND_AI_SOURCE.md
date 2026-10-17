# 0534 — Japanese bank0C phrase tables and 0504 actor AI symbolic source

Original retail Japanese Akumajou Densetsu ROM: SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28; Mapper 24 VRC6.

## Certified instruction-level source (previously credited, newly represented as assembly)

From original JP/decomp/tools/audit_ai_script_seed_0504.py: raw bank0B 71 original NMOS 6502 instructions/169 bytes, fixed PRG31 185 instructions/335 bytes; and 72 original producer-bounded table bytes (60 bank0B, 12 fixed31). All 16 historically SHA-pinned original 0504 code/data ranges are independently reauthenticated; the exact 0504 control graph must match all 504 opcode/operand bytes and 72 data bytes. These 576 bytes are NOT new strict PRG credit.

## Original indexed bank0C sound phrase structure — selectors remain unproved

The original bank0C interpreter uses LDA $A304,Y at $8B32 and LDA $A404,Y at $8D0C. Physically the first 128 entries occupy $A304–$A403 and the final 20 occupy $A404–$A42B: 148 pointers, 140 distinct ascending targets from $A42C to $A945, duplicates preserved. Every nonempty phrase interval ends in FF, final span ends $A956. The pointer table SHA256 is 2c2b1d4a4f59c39c8ad46ad4b2c103055cf61911fdd3e68e104b1a5d2cfd8945; stream SHA256 is a35de62be83954e53e65ef149ee74d5e1f95e3d1999009bcf90221bd47e7e7b5. The indexed Y selector producers are not fully bounded, so the 296 table bytes and 1323 phrase bytes are STRUCTURALLY RECONSTRUCTED CANDIDATES, not proven runtime-reachable sound semantics and not admitted as strict new bytes.

## Classified source counts

| Component | PRG bytes |
|---|---:|
| Original 6502 instruction/operand source | 14,397 |
| Typed dispatch/parser/sound/AI table bytes | 2,484 |
| Original bank04/05 sound script data | 28,200 |
| Original bank0C metadata-addressed sound pool | 3,523 |
| Secondary bounded bank0C phrase table plus pool, selector bounds unresolved | 1,619 |
| Total source represented beyond unclassified .byte | 50,223 |
| Remaining unclassified PRG | 211,921 |

Source increment 2,195: 576 original 0504 code and table source, plus 1,619 structural-candidate sound-phrase bytes. The generator still reassembles the ORIGINAL 393,232-byte JP cartridge from 17 PRG plus 8 CHR source modules exactly, checking every physical bank. Generated commercial ROM-bearing source is user-local and not committed to Git. Nine original-ROM mutation cases independently fail on changed code, sound indices, pointers and table data. GitHub CI runs ROM-free source assertions.

Reproduce:

    python3 JP/decomp/tools/test_sound_phrase_ai_0534.py
    python3 JP/decomp/tools/test_sound_phrase_ai_0534.py --rom "$ORIGINAL_JP_ROM"
    python3 JP/decomp/tools/build_whole_cart_recomp_0529.py --rom "$ORIGINAL_JP_ROM" --out /tmp/JP_0534_sources

Do not credit replay parity or novel strict PRG: historical strict PRG remains 49,504/262,144, VPP remains 27/100, semantic frontier 0508 and fixed investigation frontier FB96 remain unchanged. Next tasks: prove both indexed Y producer ranges and trace mapper-aware original callers for bank0C code after A992.