# JP0835 — Fresh original-JP Stage 1 MesenCE reference recorder

The owner does not have the old private JP0718 archive. The newly added
`jp0835_mesen_fresh_stage1_capture.lua` records a **new original-MesenCE
reference** without pretending to reconstruct the old capture.

## Source and input scope

- SHA1-authenticates the exact Japanese Mapper24 cartridge
  `a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f`.
- Starts at near-zero original Mesen frameCount and injects the
  documented three-phase JP0509 controller-only source route via
  `emu.setInput(buttons,0,0)` and `emu.setInput(buttons,0,1)`.
- Observes original CPU RAM only; no CPU/PPU/mapper writes or state edits.
- Records all input-poll intended masks and Stage1-02 endFrame
  2KiB RAM snapshots, original cycles and source-linked original type-$3D
  actors with parents 3 and 4.
- Writes private `jp0835_*_input.tsv` and `jp0835_*_ram.tsv` into the
  folder returned by `emu.getScriptDataFolder()`, never the Git repo.
- Fails closed if source 3 or 4 was never observed. It does not prove
  contact, deallocation, or bus-phase parity.

## Windows execution

From Windows PowerShell, after replacing installed MesenCE and private
ROM paths:

```powershell
& "C:\path\to\Mesen.exe" --testRunner --timeout=300 `
  --debug.scriptWindow.allowIoOsAccess=true `
  "C:\Users\hyper\CVIII-Decomp\JP\decomp\tools\jp0835_mesen_fresh_stage1_capture.lua" `
  "C:\private\Akumajou Densetsu (Japan).nes"
```

Use this exact script only; enabling script I/O permits its file writes.
The CLI switch above is documented in current MesenCE and the
I/O restriction is documented in its Lua script environment.

## Verification

Lua 5.4 parse **PASS**. A ROM-free synthetic 3,901-frame Lua callback run
created both private TSVs and passed source3/source4 presence and normal
completion. Actual MesenCE runtime/controller natural-route capture
**not executed** in the current environment.

The old `jp0834_sync_stage1_capture.py` requires an authentic JP0718
archive with 17,562 polls. It does not yet ingest this new format.
Fresh owner-Mesen/NESRecomp synchronization and frame/actor-lifetime
comparison remain separate work, not established by this recorder alone.
No ROM bytes/savestates/TSVs committed; strict PRG and VPP unchanged.
