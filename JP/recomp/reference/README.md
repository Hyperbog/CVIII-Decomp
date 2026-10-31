# NES Recomp — stable reference catalog

This directory contains the **stable Git catalog** of the Japanese ROM technical reference. The canonical master data workbook remains `NES_Recomp_Master_Reference.xlsx` in the **owner-local** `NES_Recomp_Organized/` package, together with one owner-local CSV export per subsystem (`tables/PRG.csv`, `tables/CHR.csv`, etc.).

## Non-replacement rule

- **Do not delete, rename, recreate from an empty template, or supersede** `NES_Recomp_Master_Reference.csv` with `v2`, `latest`, or another master catalog.
- Update **the same tracked CSV path** whenever a verified dataset changes. Preserve existing domain records and data provenance; change a row's count, SHA-256, verification scope, and index date only when its corresponding canonical owner-local CSV actually changes.
- Keep the XLSX workbook at its established owner-local path, editing its existing worksheets instead of replacing the workbook with a different deliverable. Preserve the existing source evidence, verification labels, and historical Git revisions.
- A CSV has no worksheets. This Git CSV is an **index**, not a substitute for the multi-tab XLSX or the full owner-local CSV tables.
- No automatic background synchronization is claimed: reference changes must be committed together with each independently verified new extraction. Repository contributors should check and update this index as part of that change.
- Public Git must not contain commercial ROM bytes, proprietary generated cartridge code, private emulator snapshots, save states, TAS recordings, or owner-local control configurations. This catalog includes hashes and counts, **not** the underlying owner-local files.
- Canonical ROM target is Japanese *Akumajou Densetsu*, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, mapper 24 / VRC6. The U.S. MMC5 version is a separate reference.

## Git cleanup boundary

The legacy `Play-Alpha.bat` and `Play-Original.bat` were identical and obsolete. The current public entry is `JP/recomp/release/alpha/Play-CVIII.bat`. The `Build-Alpha.ps1` cleanup of older private candidate shortcut names is intentionally retained. All other source and historical evidence files were preserved; similar report names do not prove duplicate content.

## Maintenance check

Run `python3 JP/recomp/reference/check_master_reference.py`. This validates the master catalog schema, unique domains, SHA formatting, nonempty evidence scope, and count. It cannot assert that private owner-local source tables have been refreshed; the contributor must do that when adding evidence.
