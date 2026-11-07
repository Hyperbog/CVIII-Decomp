# Owner-private Windows Enhanced compiled 6502 PRG acceptance.
# Keeps all game-derived binaries, ROMs, controller logs and hashes local.
[CmdletBinding()]
param(
 [string]$Rom = '',
 [Parameter(Mandatory=$true)][string]$InputReplayPath,
 [string]$CandidateDir = '',
 [string]$OutDir = '',
 [ValidateRange(1,12000)][int]$Frames = 2100,
 [ValidateSet('Enhanced','Original')][string]$Edition = 'Enhanced',
 [ValidateRange(0,100)][double]$MinCompiledPrgPercent = 90.0
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$homeBuild = Join-Path $env:USERPROFILE 'CVIII-Alpha'
if (-not $CandidateDir) {
 $local = Join-Path $PSScriptRoot 'jp_akumajou_densetsu.exe'
 $CandidateDir = if (Test-Path -LiteralPath $local -PathType Leaf) {
  $PSScriptRoot
 } else {
  Join-Path $homeBuild 'AlphaCandidate'
 }
}
$candidate = (Resolve-Path -LiteralPath $CandidateDir -ErrorAction Stop).Path
$exe = Join-Path $candidate 'jp_akumajou_densetsu.exe'
$manifestPath = Join-Path $candidate 'ALPHA_BUILD.json'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf) -or
    -not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
 throw 'Private compiled Windows game and ALPHA_BUILD.json are required in CandidateDir.'
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.original_rom_sha256 -ne '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28') {
 throw 'Private AlphaCandidate does not target the original Japanese cartridge.'
}
$exeSha = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
if ($exeSha -ne [string]$manifest.game_exe_sha256) {
 throw 'Private game executable does not match ALPHA_BUILD.json; rebuild the candidate.'
}
if (-not $Rom) {
 $hint = Join-Path $homeBuild 'LastRomPath.txt'
 if (Test-Path -LiteralPath $hint -PathType Leaf) {
  $Rom = (Get-Content -LiteralPath $hint -Raw).Trim()
 }
}
if (-not $Rom) {throw 'Specify -Rom or build once to create CVIII-Alpha/LastRomPath.txt.'}
$romPath = (Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$expected = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
if ((Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) {
 throw 'Wrong cartridge: only the exact original Japanese Mapper24 ROM is accepted.'
}
$replay = (Resolve-Path -LiteralPath $InputReplayPath -ErrorAction Stop).Path
if ((Get-Item -LiteralPath $replay).Length -eq 0) {throw 'Input replay schedule is empty.'}
$verifier = Join-Path $candidate 'Verify-Compiled.py'
if (-not (Test-Path -LiteralPath $verifier -PathType Leaf)) {
 $verifier = Join-Path $PSScriptRoot '../../tools/verify_compiled_product.py'
}
if (-not (Test-Path -LiteralPath $verifier -PathType Leaf)) {
 throw 'Missing verified Python acceptance tool; rebuild AlphaCandidate from current source.'
}
$resolver = Join-Path $candidate 'Resolve-Python.ps1'
if (-not (Test-Path -LiteralPath $resolver -PathType Leaf)) {
 $resolver = Join-Path $PSScriptRoot 'Resolve-Python.ps1'
}
if (-not (Test-Path -LiteralPath $resolver -PathType Leaf)) {
 throw 'Missing the private Alpha Python resolver.'
}
. $resolver
$py = Resolve-CviiiPython
if (-not $OutDir) {
 $OutDir = Join-Path (Join-Path $homeBuild 'CompiledAcceptance') ([guid]::NewGuid().ToString('N'))
}
$destination = [IO.Path]::GetFullPath($OutDir)
# Do not write ROM-derived machine hashes or controller provenance into Git.
$cursor = $destination
while ($cursor) {
 if (Test-Path -LiteralPath (Join-Path $cursor '.git')) {
  throw 'Private acceptance output must be outside all Git checkouts.'
 }
 $parent = [IO.Directory]::GetParent($cursor)
 if ($null -eq $parent) {break}
 $cursor = $parent.FullName
}
[IO.Directory]::CreateDirectory($destination) | Out-Null
$commandArguments = @($py.Prefix) + @($verifier, '--exe', $exe, '--rom', $romPath,
 '--input', $replay, '--out', $destination, '--frames', [string]$Frames,
 '--edition', $Edition.ToLowerInvariant(), '--min-compiled-prg-percent',
 $MinCompiledPrgPercent.ToString([Globalization.CultureInfo]::InvariantCulture))
& $py.Executable @commandArguments
if ($LASTEXITCODE -ne 0) {
 throw ('Windows Enhanced compiled execution acceptance failed; see private logs in '+$destination)
}
$resultPath = Join-Path $destination 'compiled_product_acceptance.json'
if (-not (Test-Path -LiteralPath $resultPath -PathType Leaf)) {
 throw 'The compiled acceptance command returned no machine-verified JSON.'
}
$report = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
if (-not $report.same_machine_compiled_interpreter_match -or
    [string]$report.private_executable_sha256 -ne $exeSha -or
    [int]$report.frames -ne $Frames -or
    [double]$report.compiled.compiled_prg_percent -lt $MinCompiledPrgPercent) {
 throw 'Compiled PRG acceptance result was incomplete or inconsistent.'
}
Write-Host ('PASS: '+$Frames+' '+$Edition+' frames; compiled PRG '+$report.compiled.compiled_prg_percent+'%; native and interpreter machine hashes identical.')
Write-Host ('Private report: '+$resultPath)
Write-Host 'Not a Windows GUI/save-state or original-NES hardware-parity certificate.'
