# Private Windows acceptance — Player 1 and controller/DMA

**Scope:** JP0664 on `decompilation`; Japanese mapper 24 only. The source
patch and synthetic CI have passed, but physical-controller gameplay and
independent original-game DMA parity are **not** certified. All files below
stay in the owner's private `%USERPROFILE%\CVIII-Alpha` folder.

## A. Rebuild from the merged source (not an older cached executable)

Open PowerShell in the current CVIII-Decomp repository checkout:

```powershell
git switch decompilation
git pull --ff-only origin decompilation
.\JP\recomp\release\alpha\Build-And-Play.bat -Rebuild
```

Select the original, unmodified Japanese cartridge when prompted. The
authenticated SHA-256 must be
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
If the builder uses a previous executable or fails, examine
`%USERPROFILE%\CVIII-Alpha\logs`. Never switch to the U.S. ROM.

The compiled private runtime should be:
`%USERPROFILE%\CVIII-Alpha\AlphaCandidate\jp_akumajou_densetsu.exe`.
For a packaged QA-pending product layout, run:

```powershell
py -3 JP\recomp\tools\stage_product_candidate.py --candidate "$env:USERPROFILE\CVIII-Alpha\AlphaCandidate" --out "$env:USERPROFILE\CVIII-Alpha\ProductCandidate-$(Get-Date -Format yyyyMMdd-HHmmss)"
```

That creates `game/`, `metadata/`, and `qa/` in a **new private
directory**. The existing AlphaCandidate is not modified. Play from
`game/Play-CVIII.bat`; the staged product is not publicly redistributable
and is not called release-certified.

## B. Physical gamepad test and first-cause host capture

Connect a real controller (USB or Bluetooth). Start with a fresh game,
no loaded state, default Enhanced mode and optional sprite overrides off.
Create a private session folder and run the native executable directly
to retain the host's stderr log:

```powershell
$rom = 'C:\Games\Akumajou Densetsu (Japan).nes'  # change to your actual ROM path
$game = Join-Path $env:USERPROFILE 'CVIII-Alpha\AlphaCandidate'
$qa = Join-Path $env:USERPROFILE ('CVIII-Alpha\QA\Controller-'+(Get-Date -Format yyyyMMdd-HHmmss))
New-Item -ItemType Directory -Force -Path $qa | Out-Null
Push-Location $game
try {
    $env:CVIII_CONTROLLER_ROUTE_TRACE = '1'
    & .\jp_akumajou_densetsu.exe $rom --edition enhanced --unlimited-sprites 0 --stable-sprites 0 2>&1 |
        Tee-Object -FilePath (Join-Path $qa 'Controller-Host.txt')
} finally {
    Remove-Item Env:\CVIII_CONTROLLER_ROUTE_TRACE -ErrorAction SilentlyContinue
    Pop-Location
}
```

Test separately: Start at title, Select where applicable, A, B, D-pad
left/right/up/down, left analog stick and release of every direction.
Play through the start of Stage 1, pause/resume once, then unplug/replug
the controller while the window is open if safe for the device.
Check that Player 1 retains control and no unexplained Player 2 input
appears. Compare keyboard arrows/Z/X/Enter before and after the pad test.
For exact default mapping see `JP/recomp/release/alpha/README_ALPHA.md`.

The optional `[CVIII-P1-route]` log emits at most 512 host input-evaluation
samples with `source1/pad1/buttons1` and Player 2 counterparts. NES
button bits are `80=A,40=B,20=Select,10=Start,08=Up,04=Down,02=Left,01=Right`.
This log proves the host route only: it does **not** expose serial
`$4016` read timing or DMA arbitration and must not be called bus parity.

## C. Native DMC DMA fetch capture (separate original-game session)

Use the same private ROM with original graphics/gameplay. Native
`--dmc-dma-trace` is an **executable argument**, not a
`Launch-Alpha.ps1` parameter. In PowerShell:

```powershell
Push-Location $game
try {
    & .\jp_akumajou_densetsu.exe $rom --edition enhanced --unlimited-sprites 0 --stable-sprites 0 --dmc-dma-trace (Join-Path $qa 'CVIII-DMC-DMA.csv')
} finally { Pop-Location }
py -3 JP\decomp\tools\jp_dmc_dma_trace_verify_0650.py --rom $rom --trace (Join-Path $qa 'CVIII-DMC-DMA.csv') --json (Join-Path $qa 'JP0650-DMA-summary.json')
```

Run the verifier from the **repository root** (switch back there after
the native executable exits). For strongest repeatability, use a fresh
power-on and the same scripted button schedule for reference and native
captures; manual play sessions are insufficient for cycle-by-cycle
certification. The native CSV contains ROM-derived sample bytes; keep
it local and never attach it publicly.

## D. Independent MesenCE reference and parity

The repository's JP0651 path covers **DMC sample fetches only**. It does
not yet automate complete controller serial-read or OAM DMA parity.
Build a private MesenCE at exact commit
`4b8a196e299b3de297b204fd1208d2981562c89b`, patch its pristine
`Core/NES/NesCpu.cpp` with
`JP/decomp/tools/patch_mesen_dmc_reference_0651.py`, and compile that
separate reference executable as documented in
`JP/decomp/analysis/0651_INDEPENDENT_MESEN_DMC_DMA_REFERENCE.md`.
Set the environment variable `CVIII_MESEN_DMC_TRACE` to a private CSV
path and run the same original JP ROM, NTSC region, cold start and
reproducible inputs. Then:

```powershell
py -3 JP\decomp\tools\jp_mesen_dmc_dma_compare_0651.py --rom $rom --native (Join-Path $qa 'CVIII-DMC-DMA.csv') --mesen (Join-Path $qa 'Mesen-DMC-DMA.csv') --json (Join-Path $qa 'JP0651-DMA-pair-summary.json')
```

Native and Mesen logs must contain at least two genuine DMC fetches,
with identical addresses, physical PRG offsets, sample bytes, ordering
and inter-fetch CPU-cycle gaps. If any original-game observation differs,
report the first mismatch; do **not** modify DMA timing to force a pass.
If only manual controller sessions are available, record that independent
parity is **not tested**.

## E. What to report

Record the repository commit, private EXE SHA-256, controller model,
connection type, ROM SHA-256, test steps, expected/observed Player 1
response, saved host log path, DMA verifier summary and Mesen comparison
status. Keep all ROMs, executable binaries, savestates and source-byte CSVs
private. A brief failure description with scrubbed summary statistics
is enough for a public issue; do not upload the proprietary artifacts.
