# NES Recomp — permanent Japanese ROM-only reference index

The sole permanent Git catalog is **`JP/recomp/reference/NES_Recomp_Master_Reference.csv`**. Update it **at this existing path**; never create a second master or competing version.

## Scope: Japanese VRC6 ROM-derived material only

| Domain | Records | Evidence |
| --- | ---: | --- |
| PRG | 135 | Stage/area/room pointers and effective PRG bank selectors |
| LEVELS | 130 | Room dimensions, orientation metadata and metatile spans |
| CHR | 135 | ROM-defined room CHR bank selectors and conditional baseline |
| VRC6 | 12 | ROM-defined IRQ CHR profiles, excluding observed runtime writes |
| METATILES | 1,563 | Japanese ROM metatile 4x4 tile definitions and packed palette attributes |

Canonical cartridge: *Akumajou Densetsu* (Japan), VRC6 mapper 24, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

**Excluded:** TAS movie input, controller-poll logs, emulator-generated PPU/OAM/palette snapshots, runtime mapper traces, external-document-only RAM crosswalks, and file inventories. The former VRC6 runtime write rows were removed; only 12 code-defined profiles remain.

PPU and OAM categories may return when a directly ROM-derived static dataset exists with verified ROM offsets and source evidence. Empty placeholder categories are prohibited. U.S. MMC5 mappings cannot substitute for Japanese VRC6 source evidence.

## Maintenance — preserve the permanent master

1. Update each verified owner-local `tables/<DOMAIN>.csv` **at its existing path** and keep source offsets/provenance.
2. Update the matching worksheet in the existing owner-local `NES_Recomp_Master_Reference.xlsx`.
3. Run `python3 update_rom_reference.py` locally to validate ROM-only inputs and refresh counts/checksums in the existing master CSV.
4. Commit the same Git master CSV path with new verified findings; run `python3 JP/recomp/reference/check_master_reference.py`.

GitHub CI validates the index's domain/schema policy. The underlying detailed owner-local CSVs are not in the public repository, so CI cannot verify their contents or automatically synchronize new findings. Updates occur when the extraction is made, not asynchronously.
