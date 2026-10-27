# Private AlphaCandidate-only launcher. Run after Preview-NEStudio.ps1
# has authenticated the owner's cartridge and generated NEStudio-RomPath.txt.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$romHint = Join-Path $PSScriptRoot 'NEStudio-RomPath.txt'
$launcher = Join-Path $PSScriptRoot 'Launch-Alpha.ps1'
$game = Join-Path $PSScriptRoot 'jp_akumajou_densetsu.exe'
$dll = Join-Path $PSScriptRoot 'SDL2.dll'
foreach ($file in @($romHint,$launcher,$game,$dll)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw ("Missing NEStudio private build component: " + $file +
               ". Use Build-Private-Game.bat in the NEStudio package.")
    }
}
$rom = [IO.File]::ReadAllText($romHint).Trim()
if (-not $rom -or -not (Test-Path -LiteralPath $rom -PathType Leaf)) {
    throw 'Original Japanese ROM is not at the saved owner-local location. Rebuild the private NEStudio preview.'
}
$expected = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
$actual = (Get-FileHash -LiteralPath $rom -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) {
    throw 'Wrong ROM: original Japanese Akumajou Densetsu mapper24 required.'
}
# PowerShell's call operator preserves the inherited CVIII_NESTUDIO_SESSION
# for the child native game. Do not use Start-Process -UseNewEnvironment.
& $launcher -Rom $rom -Edition Enhanced
if ($LASTEXITCODE -ne 0) {
    throw ("Native Enhanced game exited with status " + $LASTEXITCODE)
}
