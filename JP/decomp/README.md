# JP / Decomp — original-source reconstruction

This is the new **semantic decompilation** source area. The complete
research score/ledger, original 6502 mapping evidence and program lifts
remain in their established locations during the staged migration:
[canonical semantic workstream](workstreams/semantic-decompilation/README.md),
[certification state](analysis/RESUME_STATE.json),
[rigorous score rubric](docs/PROGRESS_METRIC.md), and
[existing source/tools](src).

## Moved out of the JP root — JP0662

- [asm/](asm/) — four original 6502 mnemonic modules from the old,
  misleading **JP/recomp/** directory. These are source reconstructions,
  not the real running NESRecomp game.
- [legacy/native0509/](legacy/native0509/) — original C++20 partial
  headless CPU/mapped-bus test harness, a historical reference;
  [legacy/standalone0509/](legacy/standalone0509/) — synthetic
  standalone actor and sprite source-lift test harness;
  [legacy/native_demo0510/](legacy/native_demo0510/) — superseded
  preview-authored native Stage-1-style demonstration, explicitly
  **not** the game-authentic NESRecomp product.

Their files are **not deleted**, and their historical CMake/CI
test targets continue to build at the new paths.

## Remaining source migration

The active/research-mixed `../native/enhanced`, `../tools`,
`../analysis` and `../docs` directories must be classified
per file before physical migration. They cannot be bulk moved
without updating Python parents[1]/parents[2], host build
generators, CMake, CI and historical links. These are
original-ROM research sources, **not** percentages of how
far the existing runnable native game can be played.
