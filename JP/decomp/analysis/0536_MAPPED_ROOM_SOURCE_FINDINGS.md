# 0536 — Original JP mapper-aware bank0A and bank0E room sources

## Evidence and actual source conversion

Source inputs: original Japanese mapper-24 393,232-byte retail image (SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`); previous source audits [`audit_0508_expanded.py`](../tools/audit_0508_expanded.py), [`audit_0508_bulk_0a0e.py`](../tools/audit_0508_bulk_0a0e.py) and [`audit_0508_phase5.py`](../tools/audit_0508_phase5.py). Reproducer: [`lift_bank0a_0508_0536.py`](../tools/lift_bank0a_0508_0536.py); regression gate: [`test_bank0a_0508_0536.py`](../tools/test_bank0a_0508_0536.py).

The 0508 audit accepts a **conditional** 935-instruction / 2,042-byte official-NMOS 6502 control-flow graph in VRC6 raw bank `$0A` (physical PRG 20–21). It is rooted in `$AFA4`, `$B4CC` and the four E7FB inline selector tables (`$AFA9` 20 words; `$B125` 22 words; `$B4D1` 12 words; `$B68E` 11 words). The fixed-bank `$E51E` and `$E526` routines encode selection of bank `$0A` before entering the two room-dispatch roots. The original 0508 audit does **not** prove the full runtime state/selector domain, so these source bytes are not promoted into novel strict semantic coverage.

The already-integrated 0535 state-controller source overlaps **244 instruction starts / 502 instruction bytes** and the 12-word `$B4D1` table (**24 bytes**) of this larger graph. In 0536, the source generator rejects partial instruction overlaps and omits the **exact 526 preclassified bytes**. This is an *additional unique-byte* count, not duplicate credit.

| Source kind | Newly classified physical PRG bytes | Basis |
|---|---:|---|
| Bank0A original 6502 instruction/operand mnemonics | **1,540** | 691 new starts after subtracting 0535; total original graph 935 starts / 2,042 bytes |
| Three newly source-expressed E7FB inline pointer tables | **106** | 53 original little-endian pointer words; fourth 24-byte table remains in 0535 |
| Bank0A bounded room descriptors + five indexed source pointers | **38** | `$B8A6–$B8C1` and `$B8C2–$B8CB` |
| Bank0E five conditional mapper-switched room streams | **175** | `$BE8B–$BF39` physical raw bank `$0E`, 5 records, 30 total five-byte object records, exact ROM SHA and per-record SHA |
| **Total new unique classified source** | **1,859** | Compared to actual 0535 physical source mask |

### Physical bank and data model

The conditional loader reads five source addresses (`$BEA4`, `$BEDB`, `$BF03`, `$BE8B`, `$BF1C`) from the authenticated bank `$0A` `$B8C2` table. The mapped read helper `$FB96` switches the VRC6 physical bank to `$0E` for each source byte and restores `$0A` on return. The older 0508 phase5 synthetic bus audit exercised **1,280 scenarios** (five explicitly seeded source indices and 256 different noncritical register/flag seeds each) and resolved exactly 30 five-byte objects plus five four-byte headers and five `$FF` sentinels. This is a conditional local-path proof, **not** proof that the source-index producer `$07A0` stays within `0..4` in live gameplay. The 0536 assembler emits labels and typed `.byte` records; these are genuine bounded source data, not code or a proven global object census.

### Reproducibility

```bash
python3 JP/decomp/tools/test_bank0a_0508_0536.py
python3 JP/decomp/tools/test_bank0a_0508_0536.py --rom '/path/to/Akumajou Densetsu (Japan).nes'
python3 JP/decomp/tools/build_whole_cart_recomp_0529.py --rom '/path/to/Akumajou Densetsu (Japan).nes' --out /tmp/jp0536-source
```

ROM-backed mode verifies original 0508 instruction/dispatch graph cardinalities, four pointer-table hashes, original fixed mapper-select encoded callers, descriptor boundaries, the exact five original bank0E stream hashes, no source overlap, and ten independently mutated-ROM negatives. Two-pass assembly of the **17 PRG plus 8 CHR bank sources** independently reconstructs **393,232/393,232 original iNES bytes**, original SHA intact. The commercial ROM itself is *not checked into Git*; generated `.asm` banks contain original commercial ROM data and therefore remain user-local.

### Measured status and unresolved proof

| Whole PRG source category | Checkpoint 0536 bytes |
|---|---:|
| 6502 instruction/operand mnemonics | **16,518** |
| Typed dispatch, lookup and metadata table bytes | **2,670** |
| Original bank04/05 authenticated sound script bytes | **28,200** |
| Bank0C metadata-rooted bounded pool bytes | **3,523** |
| Bank0C structurally identified sound phrase bytes (unproved selectors) | **1,619** |
| Bank0E mapper-read conditional room/object records | **175** |
| **Total PRG source-classified** | **52,705/262,144** |
| Unclassified PRG | **209,439** |

No strict PRG advancement is credited: **49,504/262,144**, VPP **27/100**, certified semantic checkpoint 0508 / fixed-CPU frontier `$FB96` unchanged. In particular, the missing live path to source index `$07A0=0..4`, global dispatch table selector bounds, and full native CPU/PPU/APU gameplay parity remain open. The existing conditional graph is now *reassemblable source*, not proof the original title executes all these paths under recorded gameplay.
