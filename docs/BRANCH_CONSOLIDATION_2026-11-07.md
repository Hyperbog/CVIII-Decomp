# Branch consolidation — 2026-11-07

## Exact operation

- Retain `decompilation` as the sole default development branch.
- Consolidation commit has the original `decompilation` head plus all 19 retired branch-tip commits as parents. Their historical Git commits remain reachable even after branch labels are removed.
- Add 254 previously missing file paths with their original Git blob content and file mode, plus the three new top-level navigation/policy documents.
- Resolve 13 overlapping newly added paths using the existing revisions listed below.
- Preserve the current `decompilation` contents for all 31 already-existing paths with differing revisions on incoming branches. In particular the current DMC/Windows fixes, product entry points and build scripts are not rolled back.

**Important:** This is a history-preserving and source-inventory consolidation, not a claim that every feature has been integrated into the running native product or that builds, reference-emulator parity or gameplay were validated. The pre-existing host source, CMake linkage, launch scripts and workflows stay unchanged. New source modules may be dormant. Alternate file revisions remain accessible from the commit's merge parents.

## Competing new paths

| Path | Version retained in consolidated tree |
| --- | --- |
| `JP/recomp/docs/WIDESCREEN_ALL_LEVELS_0829.md` | `feature/recomp-rom-layout-inventory-20261028` |
| `JP/recomp/native/enhanced/cviii_level1_world_0803.c` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_level1_world_0803.h` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_level1_world_test_0803.c` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_stage1_host_0725.c` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_stage1_host_0725.h` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_stage1_host_test_0725.c` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_stage1_join_0751.c` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_stage1_join_0751.h` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_stage1_join_test_0751.c` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/cviii_world_sprites_0807.c` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/enhanced/jp0725_test/CMakeLists.txt` | `jp0813-level1-source-world-lifetime` |
| `JP/recomp/native/rom_runtime_0732/CMakeLists.txt` | `jp0813-level1-source-world-lifetime` |

Version choices preserve the stage-world source/actor module family together and prioritize the later ROM layout inventory where that file is not present in the actor branch. They are explicit tree choices, not verified cross-feature merges.

## Remaining integration boundaries

- Lighting, weather, particles, editor and GPU sources are preserved but the default `cviii_edition.c` and main CMake integration have not been replaced with unverified competing historical versions.
- Stage-world, widescreen and original actor VM sources are preserved. Their native host/launch glue, build targets, cross-feature compatibility and real gameplay need separate source-level reconciliation and tests.
- FamiStudio/audio material and its test helpers are preserved, without declaring it an active replacement for the original sound runtime.
- The Part 17 room-header corrections to existing files, including `JP/decomp/tools/jp_room_resources_0659.py`, remain in the merge-parent history pending targeted integration.
- New historical workflows may need CI review before being treated as mandatory production gates.
- No copyrighted retail ROM, NSF or binary release file was introduced.

## Remote branch labels to delete

- `chore/jp-product-candidate-layout-20261106`
- `feature/enhanced-lighting-foundation`
- `feature/recomp-all-stage-preload-20261027`
- `feature/recomp-rom-layout-inventory-20261028`
- `feature/recomp-verified-ppu-widescreen-20261028`
- `fix/jp0650-dmc-conflict-held-cpu-observer`
- `fix/jp0651-dmc-conflict-aware-parity`
- `fix/jp0651-windows-crlf-pinned-mesen-source`
- `fix/jp-controller-first-cause-0664`
- `fix/recomp-enhanced-preview-entrypoint-20261027`
- `fix/recomp-private-release-bundle-20261027`
- `fix/recomp-widescreen-launch-target-20261027`
- `jp0664-famistudio-reference`
- `jp0711-chr-palette-evidence`
- `jp0723-ppu-queue-decoder`
- `jp0813-level1-source-world-lifetime`
- `jp-layout-stage-0663`
- `part17-jp-room-header-stage0-proof`
- `r002-public-bk2-acquisition-20261027`

These labels are safe *for Git-history retention* once the 20-parent commit is verified as the head of `decompilation`. This does not certify that every historical change is active in the working tree. **Never delete `decompilation`.** The currently available GitHub connection has no remote branch-delete action; the repository owner must remove these 19 refs.
