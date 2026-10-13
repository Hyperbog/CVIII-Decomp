# Launch private native-C11 alpha candidate in an SDL2 gameplay window.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Rom)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$romPath=(Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$expected='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
$actual=(Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) {throw 'Wrong ROM: original Japanese mapper24 cartridge required.'}
$game=Join-Path $PSScriptRoot 'jp_akumajou_densetsu.exe'
if (-not (Test-Path -LiteralPath $game) -or
    -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'SDL2.dll'))) {
 throw 'Playable SDL2 game executable is missing; first run Build-Alpha.ps1.'
}
Write-Host 'Launching windowed NESRecomp C11 VRC6 game...'
Write-Host 'Controls: arrows=D-pad, Z=A, X=B, Enter=Start, Backslash=Select.'
Push-Location $PSScriptRoot
try {
 & $game $romPath
 if ($LASTEXITCODE -ne 0) {throw "Native game exited with $LASTEXITCODE"}
} finally {Pop-Location}
