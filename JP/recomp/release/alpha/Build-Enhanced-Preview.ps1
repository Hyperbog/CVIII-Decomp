# Owner-private, visually enhanced CVIII Lighting Studio preview.
# Pinned to a separately validated feature source; leaves working Alpha untouched.
[CmdletBinding()]
param(
 [string]$Rom='',
 [string]$OutDir=(Join-Path $env:USERPROFILE 'CVIII-Enhanced-Preview'),
 [switch]$VerifyOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$expectedRom='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
$sourceCommit='2088c172668cf80fe1575ee82d5fd96ed7a9081e'
$sourceBranch='feature/enhanced-lighting-foundation'
$sourceUrl='https://github.com/Hyperbog/CVIII-Decomp.git'

if ($VerifyOnly) {
 Write-Host ('Enhanced Lighting Studio preview source: '+$sourceCommit)
 Write-Host 'Isolated, ROM-free verification only. No game built or launched.'
 return
}
foreach ($command in @('git','cmake')) {
 if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
  throw "Missing required Windows build dependency: $command"
 }
}
if (-not $Rom) {
 $hint=Join-Path (Join-Path $env:USERPROFILE 'CVIII-Alpha') 'LastRomPath.txt'
 if (Test-Path -LiteralPath $hint -PathType Leaf) {
  $previous=(Get-Content -LiteralPath $hint -Raw).Trim()
  if ($previous -and (Test-Path -LiteralPath $previous -PathType Leaf)) {
   $Rom=$previous
  }
 }
}
if (-not $Rom) {
 Add-Type -AssemblyName System.Windows.Forms
 $picker=New-Object System.Windows.Forms.OpenFileDialog
 $picker.Title='Select original Japanese Akumajou Densetsu (.nes)'
 $picker.Filter='NES cartridge (*.nes)|*.nes'
 $picker.CheckFileExists=$true
 if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
  throw 'Original Japanese cartridge not selected; no preview build started.'
 }
 $Rom=$picker.FileName
}
$romPath=(Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$romHash=(Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($romHash -ne $expectedRom) {
 throw 'Incorrect cartridge. Enhanced Preview requires the authenticated Japanese VRC6 ROM.'
}
$target=[IO.Path]::GetFullPath($OutDir)
[IO.Directory]::CreateDirectory($target) | Out-Null
$checkout=Join-Path $target '_enhanced_preview_source'
if (-not (Test-Path -LiteralPath $checkout)) {
 & git clone --branch $sourceBranch --single-branch $sourceUrl $checkout
 if ($LASTEXITCODE -ne 0) { throw 'Could not clone the Enhanced Lighting Studio preview source.' }
 & git -C $checkout checkout --detach $sourceCommit
 if ($LASTEXITCODE -ne 0) { throw 'Could not checkout the pinned Enhanced Preview commit.' }
}
if (-not (Test-Path -LiteralPath (Join-Path $checkout '.git'))) {
 throw 'Existing preview source location is not a Git checkout; refusing to overwrite.'
}
$actualSource=(& git -C $checkout rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualSource -ne $sourceCommit) {
 throw ('Preview checkout is not the authenticated source commit '+$sourceCommit+'. Refusing to replace existing files.')
}
$builder=Join-Path $checkout 'JP/recomp/release/alpha/Build-Alpha.ps1'
if (-not (Test-Path -LiteralPath $builder -PathType Leaf)) {
 throw 'Pinned Enhanced Preview source is missing its private Windows native builder.'
}
Write-Host ('CVIII Enhanced Lighting Preview commit: '+$actualSource)
Write-Host ('Private isolated build directory: '+$target)
Write-Host 'This preview includes a real Lighting Studio (Home key), lighting, weather and particle presentation.'
Write-Host 'The working CVIII-Alpha game and its saves are not modified.'
& $builder -Rom $romPath -OutDir $target -ProjectRoot $checkout -PlayAfterBuild
if (-not $?) { throw 'Enhanced Preview native build or launch failed. Inspect the private build log.' }
