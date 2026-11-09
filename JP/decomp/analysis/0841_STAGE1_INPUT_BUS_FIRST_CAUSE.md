# JP0841 — Diagnose original-JP `$4016` bus reads at the exceptional frame-3509 A pulse

## Existing original/native evidence

For the authentic original Japanese Mapper24 ROM, the JP0835 controller script requests A at source-local frame **3509**. The original Mesen endFrame CPU RAM reports A held in game-owned `$002A` at **3511**, and player integer Y `$041C` changes at **3513**. Actual JP0837 native and interpreter runs report `$002A` at **3509** and the first player-Y change at **3511**. The original player slot Y mismatch spans frames 3511–3596; the two source-3/source-4 actors still match at every sampled boundary. This is a focused input/scheduling discrepancy, not evidence that the original vertical arithmetic is wrong.

MesenCE's `InputPolled` event originates in `BaseControlManager::UpdateInputState()` and runs **after input refresh**, not at each CPU controller-port read. `NesControlManager::ReadRam()` handles the actual `$4016`/`$4017` reads separately. MesenCE recommends `emu.setInput` in the `inputPolled` event; no issue with that usage is established. The prior JP0835 `P` rows report controller intent at input refresh, **not** each CPU serial bus access.

## Bounded fresh original-Mesen capture

`JP/decomp/tools/jp0841_mesen_input_bus_firstcause.lua` uses the **verbatim JP0835 `mask_at()` function**, the same controller port assignments, a fresh power-on and the exact ROM SHA-1. It runs the existing route to local frame 3520 and writes only input/bus/write events for frames **3506–3519** into the private MesenCE LuaScriptData folder. No ROM, CPU RAM, mapper, or game-side input writes are performed. `setInput` changes only the intended controller state exactly as JP0835 already did.

- `P`: actual MesenCE input-refresh callback, `value` = intended controller P1 mask (does not establish CPU `$4016` read).
- `R`: actual CPU `$4016` or `$4017` read; callback is **after** the read and reports the bus-returned byte, not the full button mask.
- `S`: actual CPU `$4016` strobe write, logged **before** the write.
- `W`: CPU write to game-owned `$0028`, `$002A`, `$041C`, `$04DB`, `$0520`, or `$0537`, logged **before** the write.
- `E`: end-of-frame marker at MesenCE's original PPU scanline boundary; `V`: `$0028,$002A,$041C,$04DB,$0520` RAM snapshot at the same callback.

Event lines use `TYPE local_frame cpu_cycle cpu_pc cpu_address byte_value ram28 ram2a ram041c` (tab-delimited). `cpu_pc` is whatever MesenCE's CPU-state debugger exposes at callback time, not a proven bank-qualified instruction-start identity. The header pins ROM and source epoch; the `END COMPLETE` footer must be present. CPU reads must be interpreted relative to `$4016` strobe events: the low bit of an arbitrary serial read is not automatically the A button.

## Windows invocation

```powershell
cd C:\Users\hyper\CVIII-Decomp
git pull --ff-only origin decompilation
$mesen = "C:\Tools\Mesen2\Mesen.exe"
$rom = "C:\Tools\Mesen2\Akumajou Densetsu (Japan).nes"
$script = "C:\Users\hyper\CVIII-Decomp\JP\decomp\tools\jp0841_mesen_input_bus_firstcause.lua"
Test-Path $mesen
Test-Path $rom
Test-Path $script
& $mesen --testRunner --timeout=300 --debug.scriptWindow.allowIoOsAccess=true $script $rom
Get-ChildItem "$env:USERPROFILE\Documents\MesenCE\LuaScriptData" -Recurse -File -Filter "jp0841_*_bus.tsv" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 3 FullName,Length
```

Upload the latest `jp0841_*_bus.tsv` file for read/write ordering and the first `$002A` writer. Unlike JP0835, this trace is diagnostic only and cannot be passed to the existing JP0836/0837 original-state parsers. A fresh run is required; prior JP0835 RAM snapshots cannot be used to reconstruct absent `$4016` events.

**Test boundary:** Static checks reproduced the JP0835 controller-mask function exactly and verified the JavaScript-free Lua callback/API names against existing MesenCE source. The script has not been executed inside MesenCE here. Its runtime behavior, actual bus trace, and exact producer PC remain unverified.