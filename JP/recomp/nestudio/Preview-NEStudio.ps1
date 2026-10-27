# Full NEStudio owner-private game + Windows editor builder; does not overwrite CVIII-Alpha or CVIII-Lighting-Preview.
[CmdletBinding()]
param(
 [string]$Rom='',
 [string]$OutDir=(Join-Path $env:USERPROFILE 'NEStudio-Preview'),
 [switch]$BuildOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$branch='feature/nestudio-foundation'
$expected='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
if (-not $Rom) {
 $hint=Join-Path (Join-Path $env:USERPROFILE 'CVIII-Alpha') 'LastRomPath.txt'
 if (Test-Path -LiteralPath $hint) {
  $previous=(Get-Content -LiteralPath $hint -Raw).Trim()
  if ($previous -and (Test-Path -LiteralPath $previous -PathType Leaf)) { $Rom=$previous }
 }
}
if (-not $Rom) {
 Add-Type -AssemblyName System.Windows.Forms
 $dialog=New-Object System.Windows.Forms.OpenFileDialog
 $dialog.Filter='NES cartridge (*.nes)|*.nes'
 $dialog.Title='Choose your original Japanese Akumajou Densetsu ROM'
 if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
  throw 'The original Japanese ROM was not selected.'
 }
 $Rom=$dialog.FileName
}
$romPath=(Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$actual=(Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) {
 throw 'The private lighting build needs the authenticated original Japanese mapper24 ROM.'
}
$target=[IO.Path]::GetFullPath($OutDir)
[IO.Directory]::CreateDirectory($target) | Out-Null
$repo=Join-Path $target '_cviisource'
$uri='https://github.com/Hyperbog/CVIII-Decomp.git'
function Invoke-Git([string[]]$Arguments) {
 & git @Arguments
 if ($LASTEXITCODE -ne 0) { throw ('Git operation failed: '+($Arguments -join ' ')) }
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
 throw 'Git for Windows is required.'
}
if (-not (Test-Path -LiteralPath $repo)) {
 Invoke-Git -Arguments @('clone','--branch',$branch,'--single-branch',$uri,$repo)
} else {
 # This is a feature-only checkout; never switch or reset another branch.
 $current=(& git -C $repo branch --show-current)
 if ($LASTEXITCODE -ne 0 -or $current.Trim() -ne $branch) {
  throw 'The preview source folder contains a different branch. Refusing to overwrite it.'
 }
 Invoke-Git -Arguments @('-C',$repo,'pull','--ff-only','origin',$branch)
}
$commit=(& git -C $repo rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Could not identify the preview source commit.' }
Write-Host ('NEStudio source: '+$commit)
Write-Host ('Dedicated private preview folder: '+$target)
$build=Join-Path $repo 'JP/recomp/release/alpha/Build-Alpha.ps1'
if (-not (Test-Path -LiteralPath $build)) { throw 'Feature branch build tool missing.' }
& $build -Rom $romPath -OutDir $target -ProjectRoot $repo
if ($LASTEXITCODE -ne 0) {throw 'The private Enhanced game build failed.'}
# The generic Alpha player launcher can reuse an older CVIII-Alpha EXE.
# Stage a dedicated, ROM-authenticated launcher against this freshly built
# feature-branch native candidate instead of adopting that older executable.
$gameFolder=Join-Path $target 'AlphaCandidate'
$nativeExe=Join-Path $gameFolder 'jp_akumajou_densetsu.exe'
if (-not (Test-Path -LiteralPath $nativeExe -PathType Leaf)) {
 throw 'Private NEStudio native game executable was not generated.'
}
# This literal is compiled into the Windows C11 native bridge. Reject a
# plausible-looking EXE if the bridge integration was absent at build time.
$nativeBytes=[IO.File]::ReadAllBytes($nativeExe)
$nativeText=[Text.Encoding]::ASCII.GetString($nativeBytes)
if (-not $nativeText.Contains('CVIII_NESTUDIO_SESSION')) {
 throw 'Private game EXE lacks the NEStudio session bridge. Build cannot be used for live editing.'
}
Remove-Variable nativeBytes,nativeText
$launchSource=Join-Path $repo 'JP/recomp/nestudio'
foreach ($name in @('Launch-NEStudio-Game.bat','Launch-NEStudio-Game.ps1')) {
 Copy-Item -LiteralPath (Join-Path $launchSource $name) -Destination (Join-Path $gameFolder $name) -Force
}
$romHint=Join-Path $gameFolder 'NEStudio-RomPath.txt'
[IO.File]::WriteAllText($romHint,$romPath+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
Write-Host ('Bridge-compatible game launcher: '+(Join-Path $gameFolder 'Launch-NEStudio-Game.bat'))
$nestudioBuild=Join-Path $repo 'JP/recomp/nestudio/Build-NEStudio.ps1'
if (-not (Test-Path -LiteralPath $nestudioBuild)) {throw 'NEStudio desktop builder missing.'}
$argsForStudio=@{
    OutDir=(Join-Path $target 'NEStudio')
    GameFolder=(Join-Path $target 'AlphaCandidate')
}
if (-not $BuildOnly) {$argsForStudio['Launch']=$true}
& $nestudioBuild @argsForStudio
if ($LASTEXITCODE -ne 0) {throw 'NEStudio publish failed.'}
Write-Host 'NEStudio private preview ready. Existing CVIII-Alpha and lighting preview remain unchanged.'
