# CVIII JP — Checkpoint 0508 Phase 11: actual sound-$6B metadata return

**Status:** PROVISIONAL original-JP-ROM-backed, bounded 6502 execution. It **closes the prior Phase 10 synthetic-RTS dependency for this specific sound command and local initial state**; it does **not** prove full NMI/IRQ/frame reachability, runtime audio parity, an unrestricted metadata selector domain, or a completed checkpoint 0508. JP ROM: 393,232 bytes, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (mapper 24 / Konami VRC6a).

## Exact bounded path

The conditional Phase 9 state-zero initialization exits with `$19=$01`, `$68=$00`. Phase 10 examined the following raw VRC6 bank `$0A:$B58C` state-one sound command:

```asm
B58C  LDA #$6B
B58E  JSR $E249  ; save bank $0A in $25, switch bank $0C
B591  JSR $B4E9  ; set $68=0, only after real sound return
B594  INC $19   ; 1 -> 2
B596  RTS
```

**Phase 11 now executes the previously unexecuted bank-$0C:$8860–$8907 body** through its **natural `RTS`** to fixed `$E25B`. Its path is:

1. Bank `$0C:$8860–$8871`: save X/Y, `LDA $EF` ($6B), `ASL A`, read the original 16-bit pointer at `$8F5E+2*$6B=$9034` → **`$94B5`**, set `$E8/$E9`.
2. At `$94B5–$94C8` the metadata consumes **exactly 20 bytes**: bank ID `$05`, six-entry loop count `$05`, then six triples `slot, lo, hi`. The record is `05 05 00 48 BB 01 EA BB 02 42 BD 03 0A B9 04 14 BA 07 C9 BA`, SHA-256 `75cd1eb81d33ee6fb8a43eaa698720c624c16885e5fdf58b658958ba096305a4`. This physical data is raw bank `$0C`, PRG24, not yet a new byte-ledger increment.
3. For each entry, prior `$87AE` reset leaves `$0109,X=0`, so `CMP $0109,X` chooses the installation branch. Original loop code writes the pointer into `$012D,X/$0136,X`, source bank `$05` into `$06D3,X`, and sound-ID `$6B` into `$0109,X`; other fields are initialized as encoded. It then calls fixed `$E19F`.
4. **`$E19F` is executed, not simulated as a return:** it selects the bank stored at `$06D3,X` (raw bank `$05`), reads exactly the first byte from the pointer via `LDA ($E6),Y`, saves A across restoring raw bank `$0C`, and returns. All six observed first bytes are `$D9`. For slots 0,1,2,3,4,7, `$D9 >= $10` and X is neither `$05` nor `$06`; hence `$011B,X` bit 0 is initialized **zero** (alternate-parser mode for these installations). This does **not** execute their later sound streams.
5. `$88FC–$8907` decrements `$EA` from 5 to `$FF`, restores saved X/Y and executes an actual `RTS`; fixed `$E25B–$E263` resets `$26`, restores mapper bank `$0A` from saved `$25`, and returns to `$B591`; `$B4E9` resets `$68` and `$B594` increments `$19=$01→$02`. The stack reaches the synthetic parent's return destination `$9000` with the original depth restored.

| Instrument slot | Bank-$05 stream pointer | First byte | Mode bit 0 |
|---:|---:|---:|---:|
| 0 | `$BB48` | `$D9` | 0 |
| 1 | `$BBEA` | `$D9` | 0 |
| 2 | `$BD42` | `$D9` | 0 |
| 3 | `$B90A` | `$D9` | 0 |
| 4 | `$BA14` | `$D9` | 0 |
| 7 | `$BAC9` | `$D9` | 0 |

## ROM-locked execution test

`JP/decomp/tools/audit_0508_phase11.py` extends the existing Phase 10 byte-fetched partial 6502 CPU with original `ASL A`, `LDA abs,Y`, `CMP abs,X`, `DEC zp`, `BMI`, `TYA` and related operations. It rejects unsupported operations and uses the real tracked `$23` bank mapping, 6502 stack/flag operations and 8-bit indexing. It hard-checks the complete inline metadata and all six bank-$05 ROM reads, 20 metadata byte reads, instrument arrays, bank history, original sound reset order and exact final room state. No fabricated helper return is injected.

**256 seed cases × 650 original 6502 instructions = 166,400 executed instructions**; all pass. Each case has **14 mapper writes** (initial select `$0C`, six `$05→$0C` instrument reads, final restore `$0A`), six raw-bank `$05` ROM reads, one full 20-byte metadata consumption, and the existing nine APU/VRC6 sound-reset writes. Final state: `$19=2`, `$68=0`, `$18=0D`, tracked bank `$23=0A`, saved `$25=0A`, `$26=0`, and preserved incoming X/Y, `$07A0`, `$07A6` and ZP `$10`.

```sh
python3 JP/decomp/tools/audit_0508_phase11.py 'Akumajou Densetsu (Japan).nes' JP/decomp/analysis/0508_phase11_report.json
```

## Boundaries and ledger

- **R-001 OPEN:** The upstream `$18=0C/$19=13` initial conditions, two adjacent NMIs and NMI/frame interleaving remain unproved. This audit starts *conditionally at* raw bank `$0A:$B58C` in room state `$19=1`.
- **R-002 narrowed, OPEN:** State-one `$6B` installation and natural return now **really** reach `$19=2, $68=0` locally. The ensuing `$B597→$B689→$B6A4` carry gate, room indices, and actual stage liveness are separate proof obligations.
- **R-007 OPEN:** Six alternate-parser sources are installed, not executed or mixed; the APU/VRC6 writes are observable register transactions, not reference-console audio parity.
- The sound metadata/stream prefix in bank `$0C` and the bank `$05` stream roots lie in earlier analyzed bank territory. This conditional test **does not earn new semantically verified PRG bytes** absent complete live entry proof and nonoverlapping strict accounting. **New bytes 0; cumulative strict 49,404/262,144 (18.8461%); VPP 24/100; fixed PRG31 frontier `$FB96`; completed checkpoint still 0507.** No ROM is committed.
