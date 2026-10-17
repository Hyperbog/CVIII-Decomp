# Mesen2 native-Windows original-ROM headless investigation (no private media shared).
# Usage:
# powershell -ExecutionPolicy Bypass -File .\run_mesen_windows_0551.ps1 -MesenZip .\Mesen_2.2.1_Windows.zip -OriginalRom '.\Akumajou Densetsu (Japan).nes' -OutDir .\capture
param(
  [Parameter(Mandatory=$true)][string] $MesenZip,
  [Parameter(Mandatory=$true)][string] $OriginalRom,
  [Parameter(Mandatory=$true)][string] $OutDir
)
$ErrorActionPreference = 'Stop'
$expectedZip='c19e10b3b3865eb0e86e4d01bf09a5027a4452081c04b5bd5b6cbbf76e346fd6'
$expectedExe='8ef403d6b9af32075416193914d7993ce8480b347fe1f20a0cfd9815374933e7'
$expectedRom='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
$zip=(Resolve-Path -LiteralPath $MesenZip).Path
$rom=(Resolve-Path -LiteralPath $OriginalRom).Path
if((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedZip){ throw 'Unknown Mesen ZIP; refuses unverified binary' }
if((Get-FileHash -LiteralPath $rom -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedRom){ throw 'Original Japanese source ROM mismatch' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$out=(Resolve-Path -LiteralPath $OutDir).Path
$emudir=Join-Path $out 'emulator'
New-Item -ItemType Directory -Force -Path $emudir | Out-Null
Expand-Archive -LiteralPath $zip -DestinationPath $emudir -Force
$exe=Join-Path $emudir 'Mesen.exe'
if((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedExe){ throw 'Mesen executable mismatch' }
$script=Join-Path $PSScriptRoot 'mesen_windows_state13_0551.lua'
if(!(Test-Path -LiteralPath $script)){ throw 'Capture Lua script is missing' }
$stdout=Join-Path $out 'mesen_native_stdout.txt'
# Official Mesen2 CLI source documents --testRunner [lua script] [rom file] and --enableStdout.
# Requires actual Windows execution; a successful process exit alone is NOT sufficient.
& $exe --testRunner --enableStdout --timeout=180 $script $rom *> $stdout
$processExit=$LASTEXITCODE
if($processExit -ne 0){ throw "Mesen execution failed: exit $processExit (see $stdout)" }
$report=Join-Path $out 'state13_audit.json'
$auditor=Join-Path $PSScriptRoot 'audit_mesen_windows_0551.py'
$py=Get-Command py -ErrorAction SilentlyContinue
if($py){ & $py.Source -3 $auditor --stdout $stdout --rom $rom --mesen-exe $exe --out $report }
else { & python $auditor --stdout $stdout --rom $rom --mesen-exe $exe --out $report }
if($LASTEXITCODE -ne 0){ throw 'Failed provenance validation; no verified gameplay result' }
Write-Host "Authenticated Mesen report: $report"
Write-Host 'This is an original-emulator trace; it is NOT native recompilation frame parity.'
