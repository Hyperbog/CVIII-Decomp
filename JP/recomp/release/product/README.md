# Enhanced Edition — private product candidate layout

**Status: staging implemented; final gameplay and Mesen controller/DMA
acceptance pending.** This is the initial release layout, not a claim of
production completion or permission to redistribute original game assets.

The existing playable build and all previous Windows kit entry points remain
under [../alpha/](../alpha/). Product staging is additive and does not
replace an already working executable, launcher, config, save or path.

## Source-controlled structure

```text
JP/recomp/
  native/nesrecomp_cycle/    pinned external NESRecomp integration
  native/enhanced/          enhanced C11 host and optional modules
  tools/                    private builders, validators and overlays
  release/
    alpha/                  existing supported ROM-free builder kit
    product/
      README.md             stable release candidate staging contract
      QA_CONTROLLER_DMA.md  owner-only input and DMA acceptance procedure
  docs/                     feature status and product requirements
  scenarios/                input and reference replay scenarios
```

## Owner-local private product stage

On Windows, compile the actual Japanese game from the merged
`decompilation` branch using `Build-And-Play.bat -Rebuild`.
Then run from the repository root:

```powershell
py -3 JP\recomp\tools\stage_product_candidate.py --candidate "$env:USERPROFILE\CVIII-Alpha\AlphaCandidate" --out "$env:USERPROFILE\CVIII-Alpha\ProductCandidate-$(Get-Date -Format yyyyMMdd-HHmmss)"
```

The script checks the original cartridge fingerprint already stored in
`ALPHA_BUILD.json`, verifies the compiled game and private asset hashes,
and packages only the scripts enumerated by the existing Windows bundle
manifest plus required runtime files and licenses. **It does not rebuild
the game**, does not read or package the private ROM, and refuses stale,
corrupt, symlinked or pre-existing destination payloads.

```text
%USERPROFILE%\CVIII-Alpha\ProductCandidate-<timestamp>\
  game\
    jp_akumajou_densetsu.exe
    SDL2.dll
    CVIII-Assets.bin
    CVIII-CHR-Index.dat
    Play-CVIII.bat
    Launch-Alpha.ps1
    ...existing runtime scripts...
    licenses\
  metadata\
    PRODUCT_CANDIDATE.json
  qa\
    CONTROLLER_DMA.md
    ...future private test logs, never source-controlled...
```

Start `game/Play-CVIII.bat` and supply the same locally owned Japanese
ROM. The game's existing flat working directory stays intact below
`game/` so the original launcher and bundled helper scripts can run.
The stage intentionally does **not** copy private `config.ini`, control
profiles, backups, `saves/`, `*.cycstate`, QA traces or the ROM.
Such personal data remains beside the original `AlphaCandidate` or
within the owner's private folders. The product stage is a separate
build, not an in-place upgrade or save migration.

The `metadata/PRODUCT_CANDIDATE.json` records SHA-256 hashes,
immutable stage layout and explicit `qa_pending_not_certified` status.
No signed public installer, complete-game QA certification, mod SDK,
independent music/SFX mixing or widescreen support is implied.

## QA and promotion boundary

Follow [QA_CONTROLLER_DMA.md](QA_CONTROLLER_DMA.md). Physical Player 1
controller testing comes first. Independent MesenCE DMC DMA parity is a
separate acceptance gate; complete controller/OAM bus parity remains
unimplemented. Do not mark the final product or alter release status
until these real-game checks pass. Preserve source-authentication,
copyright constraints and original gameplay as the default reference.
